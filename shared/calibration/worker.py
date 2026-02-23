# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Calibration Background Worker - عامل المعايرة في الخلفية
==========================================================
Picks up queued calibration runs and executes them using BayesianCalibration.

Lifecycle:
  queued → running → succeeded | failed

On success:
  1. Creates a ``parameter_set`` with status ``candidate``
  2. Updates the run with metrics + objective_value
  3. Publishes ``sahool.calibration.run.succeeded.v1``

On failure:
  1. Updates the run with error notes
  2. Publishes ``sahool.calibration.run.failed.v1``

Usage:
    worker = CalibrationWorker(db_pool=pool, nats_client=nc)
    await worker.process_pending()  # Called by scheduler / cron / startup hook
"""

from __future__ import annotations

import json
from typing import Any

import structlog

from shared.calibration.engine import BayesianCalibration, CalibrationConfig
from shared.calibration.repository import CalibrationRepository
from shared.calibration.types import ParameterBound

logger = structlog.get_logger()

# Default parameter bounds for crop_growth model
_DEFAULT_PARAM_BOUNDS = [
    ParameterBound("rue_g_mj", 0.8, 2.5, initial=1.2),
    ParameterBound("k_extinction", 0.3, 0.8, initial=0.5),
    ParameterBound("base_temp_c", 0.0, 8.0, initial=4.0),
    ParameterBound("gdd_maturity", 1200, 2800, initial=2000),
    ParameterBound("max_lai", 3.0, 9.0, initial=6.0),
    ParameterBound("harvest_index", 0.25, 0.55, initial=0.42),
    ParameterBound("sla_cm2_g", 12.0, 35.0, initial=20.0),
]


class CalibrationWorker:
    """
    Background worker that processes queued calibration runs.
    عامل خلفي يعالج تشغيلات المعايرة المنتظرة.
    """

    def __init__(
        self,
        db_pool: Any,
        nats_client: Any = None,
        n_trials: int = 60,
    ) -> None:
        self._pool = db_pool
        self._nats = nats_client
        self._n_trials = n_trials
        self._repo = CalibrationRepository(db_pool=db_pool)

    async def process_pending(self, *, max_runs: int = 5) -> list[str]:
        """
        Process up to ``max_runs`` queued calibration runs.
        معالجة ما يصل إلى ``max_runs`` تشغيل معايرة منتظر.

        Returns list of run IDs that were processed.
        """
        if self._pool is None:
            logger.warning("calibration_worker_no_pool")
            return []

        processed: list[str] = []

        # Fetch queued runs
        sql = """
        SELECT id::text, tenant_id, field_id, season_id, crop_type,
               model_name, model_version, method, dataset_fingerprint
        FROM calibration_run
        WHERE status = 'queued'
        ORDER BY started_at ASC
        LIMIT $1
        """
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(sql, max_runs)

        for row in rows:
            run_id = row["id"]
            try:
                await self._process_one(dict(row))
                processed.append(run_id)
            except Exception as exc:
                logger.error(
                    "calibration_worker_run_failed",
                    run_id=run_id,
                    error=str(exc),
                )
                await self._repo.update_run_status(
                    run_id, "failed", notes=str(exc)[:500]
                )
                await self._publish_event(
                    "sahool.calibration.run.failed.v1",
                    {"run_id": run_id, "error": str(exc)[:200]},
                )

        if processed:
            logger.info("calibration_worker_batch_done", processed=len(processed))
        return processed

    async def _process_one(self, run: dict[str, Any]) -> None:
        """Execute a single calibration run end-to-end."""
        run_id = run["id"]

        # 1. Transition to running
        await self._repo.update_run_status(run_id, "running")
        await self._publish_event(
            "sahool.calibration.run.started.v1",
            {"run_id": run_id, "tenant_id": run["tenant_id"]},
        )

        logger.info(
            "calibration_worker_run_started",
            run_id=run_id,
            field_id=run["field_id"],
            season_id=run["season_id"],
        )

        # 2. Build predictor from DB
        from shared.calibration.adapters.build_predictor import build_predictor_from_db

        predictor_instance = await build_predictor_from_db(
            tenant_id=run["tenant_id"],
            field_id=run["field_id"],
            season_id=run["season_id"],
            pool=self._pool,
        )

        # 3. Load observation targets from the run's dataset
        targets = await self._load_targets(run)
        if not targets:
            await self._repo.update_run_status(
                run_id, "failed", notes="No observation targets found"
            )
            return

        # 4. Split into train/holdout (80/20)
        from shared.calibration.types import CalibrationTarget

        train_targets: list[CalibrationTarget] = []
        holdout_targets: list[CalibrationTarget] = []

        for tgt in targets:
            n_obs = len(tgt.observations)
            split = max(1, int(n_obs * 0.8))
            train_targets.append(
                CalibrationTarget(
                    variable=tgt.variable,
                    observations=tgt.observations[:split],
                    weight=tgt.weight,
                    min_quality_score=tgt.min_quality_score,
                )
            )
            if split < n_obs:
                holdout_targets.append(
                    CalibrationTarget(
                        variable=tgt.variable,
                        observations=tgt.observations[split:],
                        weight=tgt.weight,
                        min_quality_score=tgt.min_quality_score,
                    )
                )

        # 5. Run Bayesian calibration
        config = CalibrationConfig(
            n_trials=self._n_trials,
            seed=42,
        )
        cal = BayesianCalibration(
            predictor=predictor_instance.predict,
            param_space=_DEFAULT_PARAM_BOUNDS,
            config=config,
        )
        output = cal.calibrate(
            targets=train_targets,
            holdout_targets=holdout_targets or None,
        )

        # 6. Update run with results
        metrics = {
            "validation_rmse": {k: round(v, 4) for k, v in output.validation.rmse.items()},
            "validation_mae": {k: round(v, 4) for k, v in output.validation.mae.items()},
            "validation_bias": {k: round(v, 4) for k, v in output.validation.bias.items()},
            "safe_for_decision": output.safe_for_decision,
            "gate_violations": output.gate_violations,
            "objective_breakdown": {k: round(v, 4) for k, v in output.objective_breakdown.items()},
        }
        await self._repo.update_run_status(
            run_id,
            "succeeded",
            metrics=metrics,
            objective_value=output.best_objective,
        )

        # 7. GAP-10: Auto-persist as candidate parameter set
        ps_id = await self._repo.create_parameter_set({
            "tenant_id": run["tenant_id"],
            "field_id": run["field_id"],
            "season_id": run["season_id"],
            "model_name": run["model_name"],
            "model_version": run["model_version"],
            "parameters": output.best_params,
            "param_uncertainty": {},
            "prior": {},
            "posterior_summary": metrics,
            "created_from_run_id": run_id,
        })

        logger.info(
            "calibration_worker_run_succeeded",
            run_id=run_id,
            parameter_set_id=ps_id,
            objective=round(output.best_objective, 4),
            safe=output.safe_for_decision,
        )

        # 8. Publish success event
        await self._publish_event(
            "sahool.calibration.run.succeeded.v1",
            {
                "run_id": run_id,
                "tenant_id": run["tenant_id"],
                "field_id": run["field_id"],
                "season_id": run["season_id"],
                "parameter_set_id": ps_id,
                "objective_value": round(output.best_objective, 4),
                "safe_for_decision": output.safe_for_decision,
                "best_params": {k: round(v, 4) for k, v in output.best_params.items()},
            },
        )

    async def _load_targets(self, run: dict[str, Any]) -> list:
        """
        Load calibration targets from field observations in DB.
        تحميل أهداف المعايرة من أرصاد الحقل في قاعدة البيانات.
        """
        from shared.calibration.types import CalibrationObservation, CalibrationTarget

        sql = """
        SELECT obs_type, day::text AS t, value, quality
        FROM field_observation
        WHERE tenant_id = $1 AND field_id = $2
          AND obs_type IN ('ndvi', 'lai', 'biomass', 'soil_moisture')
        ORDER BY day
        """
        try:
            async with self._pool.acquire() as conn:
                rows = await conn.fetch(
                    sql, run["tenant_id"], run["field_id"]
                )
        except Exception as exc:
            logger.warning("calibration_load_targets_failed", error=str(exc))
            return []

        if not rows:
            return []

        # Group by variable
        groups: dict[str, list[CalibrationObservation]] = {}
        for r in rows:
            var = r["obs_type"]
            # Map NDVI to LAI using Beer-Lambert
            if var == "ndvi":
                from shared.digital_twin.adapters import ndvi_to_lai_estimate
                val = ndvi_to_lai_estimate(r["value"])
                var = "LAI"
            elif var == "lai":
                val = r["value"]
                var = "LAI"
            else:
                val = r["value"]

            groups.setdefault(var, []).append(
                CalibrationObservation(
                    t=r["t"][:10],
                    value=val,
                    uncertainty=max(0.05, 1.0 - float(r.get("quality", 0.7))),
                )
            )

        return [
            CalibrationTarget(variable=var, observations=obs, weight=1.0)
            for var, obs in groups.items()
            if len(obs) >= 3  # minimum 3 observations per variable
        ]

    async def _publish_event(self, subject: str, payload: dict[str, Any]) -> None:
        """Publish a NATS event (best-effort)."""
        if self._nats is None:
            return
        try:
            from datetime import datetime, timezone
            payload["ts"] = datetime.now(timezone.utc).isoformat()
            await self._nats.publish(subject, json.dumps(payload).encode())
        except Exception as exc:
            logger.warning("calibration_worker_nats_failed", subject=subject, error=str(exc))
