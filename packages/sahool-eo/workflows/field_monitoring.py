"""
🌾 SAHOOL Field Monitoring Workflow
سير عمل مراقبة الحقول

This workflow provides complete field monitoring pipeline:
1. Fetch satellite data (Sentinel-2)
2. Apply cloud masking
3. Calculate vegetation indices
4. Assess crop health
5. Export to SAHOOL format

Corresponds to Event Chain 1 in SAHOOL architecture:
satellite-service → indicators-service → crop-health-ai → yield-engine
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class FieldMonitoringWorkflow:
    """
    Complete field monitoring workflow using eo-learn

    This workflow orchestrates the full processing pipeline for
    agricultural field monitoring, from satellite data acquisition
    to health assessment and event generation.

    Example:
        from sahool_eo import SahoolEOClient, FieldMonitoringWorkflow

        client = SahoolEOClient()
        workflow = FieldMonitoringWorkflow(client)

        result = workflow.execute(
            field_id="field_001",
            tenant_id="tenant_123",
            bbox=(44.0, 15.0, 44.5, 15.5),
            time_interval=("2024-01-01", "2024-01-31")
        )

        # Access results
        print(result["health_assessment"])
        print(result["indices"])
    """

    def __init__(
        self,
        client=None,
        config=None,
        resolution: int = 10,
        max_cloud_coverage: float = 30.0,
        cloud_mask_buffer: int = 2,
        indices: Optional[List[str]] = None,
    ):
        """
        Initialize field monitoring workflow

        Args:
            client: SahoolEOClient instance
            config: SentinelHubConfig (used if client is None)
            resolution: Target resolution in meters
            max_cloud_coverage: Maximum cloud coverage percentage
            cloud_mask_buffer: Buffer around clouds in pixels
            indices: List of indices to calculate (None = all)
        """
        self.client = client
        self.config = config
        self.resolution = resolution
        self.max_cloud_coverage = max_cloud_coverage
        self.cloud_mask_buffer = cloud_mask_buffer
        self.indices = indices or ["NDVI", "EVI", "LAI", "NDWI", "SAVI", "NDMI"]

    def execute(
        self,
        field_id: str,
        tenant_id: str,
        bbox: Tuple[float, float, float, float],
        time_interval: Tuple[str, str],
        generate_events: bool = True,
    ) -> Dict[str, Any]:
        """
        Execute field monitoring workflow

        Args:
            field_id: SAHOOL field identifier
            tenant_id: SAHOOL tenant identifier
            bbox: Bounding box (min_lon, min_lat, max_lon, max_lat)
            time_interval: (start_date, end_date) in YYYY-MM-DD format
            generate_events: Generate SAHOOL events for message bus

        Returns:
            Dictionary with monitoring results
        """
        logger.info(f"Starting field monitoring for {field_id}")

        result = {
            "field_id": field_id,
            "tenant_id": tenant_id,
            "workflow": "field_monitoring",
            "execution_start": datetime.utcnow().isoformat(),
            "status": "running",
            "steps": [],
        }

        try:
            # Step 1: Fetch satellite data
            logger.info("Step 1: Fetching satellite data...")
            eopatch = self._fetch_data(bbox, time_interval)
            result["steps"].append(
                {
                    "name": "fetch_data",
                    "status": "completed",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

            if eopatch is None:
                result["status"] = "failed"
                result["error"] = "No satellite data available"
                return result

            # Step 2: Apply cloud masking
            logger.info("Step 2: Applying cloud mask...")
            eopatch = self._apply_cloud_mask(eopatch)
            result["steps"].append(
                {
                    "name": "cloud_mask",
                    "status": "completed",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

            # Step 3: Calculate vegetation indices
            logger.info("Step 3: Calculating vegetation indices...")
            eopatch = self._calculate_indices(eopatch)
            result["steps"].append(
                {
                    "name": "calculate_indices",
                    "status": "completed",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

            # Step 4: Export to SAHOOL format
            logger.info("Step 4: Exporting results...")
            export_result = self._export_results(eopatch, field_id, tenant_id)
            result["steps"].append(
                {
                    "name": "export",
                    "status": "completed",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

            # Add results
            result["indices"] = export_result.get("indices", {})
            result["health_assessment"] = export_result.get("health_assessment", {})
            result["metadata"] = export_result.get("metadata", {})

            # Step 5: Generate events if requested
            if generate_events:
                logger.info("Step 5: Generating SAHOOL events...")
                events = self._generate_events(eopatch, field_id, tenant_id)
                result["events"] = events
                result["steps"].append(
                    {
                        "name": "generate_events",
                        "status": "completed",
                        "timestamp": datetime.utcnow().isoformat(),
                        "events_count": len(events),
                    }
                )

            result["status"] = "completed"
            result["execution_end"] = datetime.utcnow().isoformat()

            logger.info(f"Field monitoring completed for {field_id}")
            return result

        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            result["status"] = "failed"
            result["error"] = str(e)
            result["execution_end"] = datetime.utcnow().isoformat()
            return result

    def _fetch_data(self, bbox, time_interval):
        """Fetch satellite data"""
        from sentinelhub import CRS, BBox

        from ..tasks.fetch import SahoolSentinelFetchTask

        # Create bbox object
        sh_bbox = BBox(bbox=bbox, crs=CRS.WGS84)

        # Create and execute fetch task
        fetch_task = SahoolSentinelFetchTask(
            resolution=self.resolution,
            max_cloud_coverage=self.max_cloud_coverage,
            config=self.config,
        )

        return fetch_task.execute(sh_bbox, time_interval)

    def _apply_cloud_mask(self, eopatch):
        """Apply cloud masking"""
        from ..tasks.cloud_mask import SahoolCloudMaskTask

        mask_task = SahoolCloudMaskTask(
            buffer_size=self.cloud_mask_buffer,
        )

        return mask_task.execute(eopatch)

    def _calculate_indices(self, eopatch):
        """Calculate vegetation indices"""
        from ..tasks.indices import AllIndicesTask

        indices_task = AllIndicesTask(
            indices=self.indices,
        )

        return indices_task.execute(eopatch)

    def _export_results(self, eopatch, field_id: str, tenant_id: str):
        """Export results to SAHOOL format"""
        from ..tasks.export import SahoolExportTask

        export_task = SahoolExportTask(
            field_id=field_id,
            tenant_id=tenant_id,
        )

        return export_task.execute(eopatch)

    def _generate_events(
        self, eopatch, field_id: str, tenant_id: str
    ) -> List[Dict[str, Any]]:
        """Generate SAHOOL events"""
        from ..tasks.export import EOPatchToSahoolTask
        from ..tasks.indices import AllIndicesTask

        # Get indices summary
        indices_task = AllIndicesTask()
        summary = indices_task.get_summary(eopatch)

        # Create events
        event_task = EOPatchToSahoolTask(
            field_id=field_id,
            tenant_id=tenant_id,
        )

        return event_task.execute(eopatch, summary)


class BatchFieldMonitoringWorkflow:
    """
    Batch processing workflow for multiple fields

    Efficiently processes multiple fields in parallel or sequence,
    with error handling and progress tracking.
    """

    def __init__(self, client=None, max_workers: int = 4):
        """
        Initialize batch workflow

        Args:
            client: SahoolEOClient instance
            max_workers: Maximum parallel workers
        """
        self.client = client
        self.max_workers = max_workers
        self.workflow = FieldMonitoringWorkflow(client)

    def execute(
        self,
        fields: List[Dict[str, Any]],
        tenant_id: str,
        time_interval: Tuple[str, str],
    ) -> Dict[str, Any]:
        """
        Execute batch monitoring for multiple fields

        Args:
            fields: List of field configs with 'field_id' and 'bbox'
            tenant_id: SAHOOL tenant identifier
            time_interval: (start_date, end_date)

        Returns:
            Batch processing results
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed

        results = {
            "tenant_id": tenant_id,
            "execution_start": datetime.utcnow().isoformat(),
            "total_fields": len(fields),
            "completed": 0,
            "failed": 0,
            "fields": [],
        }

        def process_field(field_config):
            field_id = field_config["field_id"]
            bbox = field_config["bbox"]

            try:
                result = self.workflow.execute(
                    field_id=field_id,
                    tenant_id=tenant_id,
                    bbox=bbox,
                    time_interval=time_interval,
                )
                return {"field_id": field_id, "status": "success", "result": result}
            except Exception as e:
                logger.error(f"Failed to process {field_id}: {e}")
                return {"field_id": field_id, "status": "error", "error": str(e)}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(process_field, field): field for field in fields}

            for future in as_completed(futures):
                field_result = future.result()
                results["fields"].append(field_result)

                if field_result["status"] == "success":
                    results["completed"] += 1
                else:
                    results["failed"] += 1

        results["execution_end"] = datetime.utcnow().isoformat()
        return results
