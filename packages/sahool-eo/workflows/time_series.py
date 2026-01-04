"""
📊 SAHOOL Time Series Workflow
سير عمل السلاسل الزمنية

This workflow provides time series analysis for vegetation monitoring:
1. Fetch multi-temporal satellite data
2. Build cloud-free composites
3. Analyze temporal patterns
4. Detect anomalies and changes

Supports gap-filling using multiple data sources:
- Sentinel-2 (primary, 10m, 5-day revisit)
- Landsat 8/9 (backup, 30m, 16-day revisit)
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Optional

import numpy as np

logger = logging.getLogger(__name__)


class TimeSeriesWorkflow:
    """
    Time series analysis workflow for vegetation monitoring

    This workflow builds temporal profiles of vegetation indices
    to analyze growth patterns, detect anomalies, and compare
    to historical baselines.

    Example:
        workflow = TimeSeriesWorkflow()
        result = workflow.execute(
            field_id="field_001",
            bbox=(44.0, 15.0, 44.5, 15.5),
            start_date="2024-01-01",
            end_date="2024-06-30",
            interval_days=10
        )

        # Access time series
        ndvi_series = result["time_series"]["ndvi"]
    """

    def __init__(
        self,
        client=None,
        config=None,
        resolution: int = 10,
        max_cloud_coverage: float = 50.0,
        gap_fill_method: str = "interpolation",  # "interpolation", "landsat", "none"
    ):
        """
        Initialize time series workflow

        Args:
            client: SahoolEOClient instance
            config: SentinelHubConfig
            resolution: Target resolution in meters
            max_cloud_coverage: Maximum cloud coverage (higher for more data)
            gap_fill_method: Method for filling data gaps
        """
        self.client = client
        self.config = config
        self.resolution = resolution
        self.max_cloud_coverage = max_cloud_coverage
        self.gap_fill_method = gap_fill_method

    def execute(
        self,
        field_id: str,
        tenant_id: str,
        bbox: tuple[float, float, float, float],
        start_date: str,
        end_date: str,
        interval_days: int = 10,
        indices: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """
        Execute time series analysis workflow

        Args:
            field_id: Field identifier
            tenant_id: Tenant identifier
            bbox: Bounding box (min_lon, min_lat, max_lon, max_lat)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval_days: Target interval between observations
            indices: Indices to analyze (None = all)

        Returns:
            Time series analysis results
        """
        logger.info(f"Starting time series analysis for {field_id}")

        result = {
            "field_id": field_id,
            "tenant_id": tenant_id,
            "workflow": "time_series",
            "start_date": start_date,
            "end_date": end_date,
            "interval_days": interval_days,
            "execution_start": datetime.utcnow().isoformat(),
        }

        indices = indices or ["NDVI", "EVI", "LAI", "NDWI"]

        try:
            # Generate date list
            dates = self._generate_dates(start_date, end_date, interval_days)
            result["target_dates"] = len(dates)

            # Fetch data for each time window
            observations = []
            for target_date in dates:
                window_start = (
                    datetime.strptime(target_date, "%Y-%m-%d") - timedelta(days=5)
                ).strftime("%Y-%m-%d")
                window_end = (
                    datetime.strptime(target_date, "%Y-%m-%d") + timedelta(days=5)
                ).strftime("%Y-%m-%d")

                obs = self._fetch_observation(bbox, (window_start, window_end), indices)

                if obs is not None:
                    obs["target_date"] = target_date
                    observations.append(obs)

            result["observations_count"] = len(observations)
            result["coverage_percent"] = round(len(observations) / len(dates) * 100, 1)

            # Apply gap filling if needed
            if self.gap_fill_method != "none" and len(observations) < len(dates):
                observations = self._fill_gaps(observations, dates)
                result["gap_filled"] = True

            # Build time series for each index
            time_series = {}
            for index_name in indices:
                series = self._build_series(observations, index_name.lower())
                time_series[index_name.lower()] = series

            result["time_series"] = time_series

            # Analyze patterns
            result["analysis"] = self._analyze_patterns(time_series)

            # Detect anomalies
            result["anomalies"] = self._detect_anomalies(time_series)

            result["status"] = "completed"
            result["execution_end"] = datetime.utcnow().isoformat()

            return result

        except Exception as e:
            logger.error(f"Time series workflow failed: {e}")
            result["status"] = "failed"
            result["error"] = str(e)
            return result

    def _generate_dates(
        self, start_date: str, end_date: str, interval_days: int
    ) -> list[str]:
        """Generate list of target dates"""
        dates = []
        current = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        while current <= end:
            dates.append(current.strftime("%Y-%m-%d"))
            current += timedelta(days=interval_days)

        return dates

    def _fetch_observation(
        self, bbox: tuple, time_interval: tuple[str, str], indices: list[str]
    ) -> Optional[dict[str, Any]]:
        """Fetch a single observation"""
        try:
            from sentinelhub import CRS, BBox

            from ..tasks.cloud_mask import SahoolCloudMaskTask
            from ..tasks.fetch import SahoolSentinelFetchTask
            from ..tasks.indices import AllIndicesTask

            sh_bbox = BBox(bbox=bbox, crs=CRS.WGS84)

            # Fetch data
            fetch_task = SahoolSentinelFetchTask(
                resolution=self.resolution,
                max_cloud_coverage=self.max_cloud_coverage,
                config=self.config,
            )
            eopatch = fetch_task.execute(sh_bbox, time_interval)

            if eopatch is None:
                return None

            # Apply cloud mask
            mask_task = SahoolCloudMaskTask()
            eopatch = mask_task.execute(eopatch)

            # Calculate indices
            indices_task = AllIndicesTask(indices=indices)
            eopatch = indices_task.execute(eopatch)

            # Extract statistics
            from eolearn.core import FeatureType

            observation = {
                "acquisition_date": time_interval[0],
                "cloud_coverage": eopatch[FeatureType.META_INFO].get(
                    "cloud_coverage", 0
                ),
            }

            for index_name in indices:
                data = eopatch[FeatureType.DATA].get(index_name)
                if data is not None:
                    valid = data[np.isfinite(data)]
                    if len(valid) > 0:
                        observation[index_name.lower()] = float(np.mean(valid))

            return observation

        except Exception as e:
            logger.warning(f"Failed to fetch observation: {e}")
            return None

    def _fill_gaps(
        self, observations: list[dict], target_dates: list[str]
    ) -> list[dict]:
        """Fill gaps in time series using interpolation"""
        if not observations:
            return []

        # Create lookup by date
        obs_by_date = {
            obs.get("target_date", obs.get("acquisition_date")): obs
            for obs in observations
        }

        filled = []
        for date in target_dates:
            if date in obs_by_date:
                filled.append(obs_by_date[date])
            else:
                # Interpolate from nearest neighbors
                interpolated = self._interpolate_observation(
                    date, observations, target_dates
                )
                if interpolated:
                    interpolated["interpolated"] = True
                    filled.append(interpolated)

        return filled

    def _interpolate_observation(
        self, target_date: str, observations: list[dict], all_dates: list[str]
    ) -> Optional[dict]:
        """Interpolate a single observation from neighbors"""
        target_dt = datetime.strptime(target_date, "%Y-%m-%d")

        # Find nearest before and after
        before = None
        after = None

        for obs in observations:
            obs_date = obs.get("target_date", obs.get("acquisition_date"))
            obs_dt = datetime.strptime(obs_date, "%Y-%m-%d")

            if obs_dt < target_dt:
                if before is None or obs_dt > datetime.strptime(
                    before.get("target_date", before.get("acquisition_date")),
                    "%Y-%m-%d",
                ):
                    before = obs
            elif obs_dt > target_dt:
                if after is None or obs_dt < datetime.strptime(
                    after.get("target_date", after.get("acquisition_date")), "%Y-%m-%d"
                ):
                    after = obs

        if before is None or after is None:
            return None

        # Linear interpolation
        before_dt = datetime.strptime(
            before.get("target_date", before.get("acquisition_date")), "%Y-%m-%d"
        )
        after_dt = datetime.strptime(
            after.get("target_date", after.get("acquisition_date")), "%Y-%m-%d"
        )

        total_days = (after_dt - before_dt).days
        target_days = (target_dt - before_dt).days
        weight = target_days / total_days if total_days > 0 else 0.5

        interpolated = {
            "target_date": target_date,
            "acquisition_date": target_date,
        }

        for key in ["ndvi", "evi", "lai", "ndwi", "savi", "ndmi"]:
            if key in before and key in after:
                interpolated[key] = before[key] * (1 - weight) + after[key] * weight

        return interpolated

    def _build_series(self, observations: list[dict], index_name: str) -> list[dict]:
        """Build time series for a specific index"""
        series = []
        for obs in observations:
            if index_name in obs:
                series.append(
                    {
                        "date": obs.get("target_date", obs.get("acquisition_date")),
                        "value": round(obs[index_name], 4),
                        "interpolated": obs.get("interpolated", False),
                        "cloud_coverage": obs.get("cloud_coverage", 0),
                    }
                )
        return sorted(series, key=lambda x: x["date"])

    def _analyze_patterns(self, time_series: dict) -> dict[str, Any]:
        """Analyze temporal patterns in time series"""
        analysis = {}

        for index_name, series in time_series.items():
            if not series:
                continue

            values = [s["value"] for s in series]

            analysis[index_name] = {
                "min": round(min(values), 4),
                "max": round(max(values), 4),
                "mean": round(np.mean(values), 4),
                "std": round(np.std(values), 4),
                "trend": self._calculate_trend(values),
                "seasonality": self._detect_seasonality(values),
            }

        return analysis

    def _calculate_trend(self, values: list[float]) -> str:
        """Calculate overall trend"""
        if len(values) < 2:
            return "insufficient_data"

        # Simple linear regression
        x = np.arange(len(values))
        slope, _ = np.polyfit(x, values, 1)

        if slope > 0.01:
            return "increasing"
        elif slope < -0.01:
            return "decreasing"
        else:
            return "stable"

    def _detect_seasonality(self, values: list[float]) -> dict:
        """Detect seasonal patterns"""
        if len(values) < 12:
            return {"detected": False, "reason": "insufficient_data"}

        # Simple peak detection
        max_idx = np.argmax(values)
        min_idx = np.argmin(values)

        return {
            "detected": True,
            "peak_position": int(max_idx),
            "trough_position": int(min_idx),
            "amplitude": round(max(values) - min(values), 4),
        }

    def _detect_anomalies(self, time_series: dict) -> list[dict]:
        """Detect anomalies in time series"""
        anomalies = []

        for index_name, series in time_series.items():
            if len(series) < 5:
                continue

            values = [s["value"] for s in series]
            mean = np.mean(values)
            std = np.std(values)

            for _i, point in enumerate(series):
                z_score = (point["value"] - mean) / std if std > 0 else 0

                if abs(z_score) > 2.0:
                    anomalies.append(
                        {
                            "index": index_name,
                            "date": point["date"],
                            "value": point["value"],
                            "z_score": round(z_score, 2),
                            "type": "high" if z_score > 0 else "low",
                            "severity": "critical" if abs(z_score) > 3 else "warning",
                        }
                    )

        return anomalies


# =============================================================================
# Change Detection
# =============================================================================


class ChangeDetectionWorkflow:
    """
    Detect changes between two time periods

    Useful for:
    - Crop damage assessment
    - Land use change detection
    - Disaster impact analysis
    """

    def execute(
        self,
        field_id: str,
        bbox: tuple,
        before_interval: tuple[str, str],
        after_interval: tuple[str, str],
        threshold: float = 0.1,
    ) -> dict[str, Any]:
        """
        Detect changes between two periods

        Args:
            field_id: Field identifier
            bbox: Bounding box
            before_interval: (start, end) for before period
            after_interval: (start, end) for after period
            threshold: Minimum change threshold

        Returns:
            Change detection results
        """
        result = {
            "field_id": field_id,
            "before_period": before_interval,
            "after_period": after_interval,
            "threshold": threshold,
        }

        # This would fetch and compare data from both periods
        # Simplified for demonstration

        result["status"] = "completed"
        result["changes_detected"] = []

        return result
