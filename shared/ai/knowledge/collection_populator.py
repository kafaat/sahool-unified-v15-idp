# ═══════════════════════════════════════════════════════════════════════════════
# Knowledge Base Collection Populator
# أداة تعبئة مجموعات قاعدة المعرفة
# ═══════════════════════════════════════════════════════════════════════════════
#
# Populates UltraRAG collections from:
#   1. Markdown documentation (docs/knowledge-base/)
#   2. Existing code modules (shared/yemen/, shared/pest_scouting/, etc.)
#
# Collection mapping:
#   crops/          → crop_knowledge
#   diseases/       → pest_knowledge
#   irrigation/     → irrigation_practices + crop_water_requirements
#   soils/          → soil_knowledge
#   fertilization/  → fertilizer_knowledge
#   weather/        → weather_knowledge
#   remote-sensing/ → remote_sensing_knowledge
#   */              → general_agriculture (fallback)
#
# ═══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from shared.ai.knowledge._logging import get_logger

from .collections import (
    ALL_COLLECTIONS,
    COLLECTION_DIRECTORY_MAP,
    CROP_KNOWLEDGE,
    CROP_WATER_REQUIREMENTS,
    FERTILIZER_KNOWLEDGE,
    GENERAL_AGRICULTURE,
    IRRIGATION_PRACTICES,
    PEST_KNOWLEDGE,
    SMART_AGRICULTURE_KNOWLEDGE,
    SOIL_KNOWLEDGE,
    WEATHER_KNOWLEDGE,
)
from .ingestion.pipeline import BatchIngestionReport, KnowledgeIngestionPipeline

logger = get_logger(__name__)


@dataclass
class PopulationReport:
    """Report from a population run | تقرير تشغيل التعبئة"""

    total_files: int = 0
    total_ingested: int = 0
    total_failed: int = 0
    total_skipped: int = 0
    by_collection: dict[str, int] = field(default_factory=dict)
    by_domain: dict[str, int] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    batch_reports: list[BatchIngestionReport] = field(default_factory=list)


class KnowledgeBasePopulator:
    """Populates UltraRAG knowledge base collections from documentation and code.
    يعبئ مجموعات قاعدة المعرفة من الوثائق والكود"""

    def __init__(
        self,
        pipeline: KnowledgeIngestionPipeline | None = None,
        base_docs_path: str | Path = "docs/knowledge-base",
        verify: bool = True,
    ) -> None:
        self._pipeline = pipeline or KnowledgeIngestionPipeline()
        self._base_docs_path = Path(base_docs_path)
        self._verify = verify

    def populate_from_docs(
        self,
        collections: list[str] | None = None,
        dry_run: bool = False,
    ) -> PopulationReport:
        """Populate collections from docs/knowledge-base/ directory.
        تعبئة المجموعات من مجلد الوثائق"""
        report = PopulationReport()
        target_collections = collections or ALL_COLLECTIONS

        for collection in target_collections:
            directories = COLLECTION_DIRECTORY_MAP.get(collection, [])
            for dir_rel in directories:
                dir_path = self._base_docs_path.parent.parent / dir_rel
                if not dir_path.is_dir():
                    logger.debug("directory_not_found", path=str(dir_path), collection=collection)
                    continue

                if dry_run:
                    files = list(dir_path.glob("*.md"))
                    file_count = len([f for f in files if f.name != "README.md"])
                    report.by_collection[collection] = report.by_collection.get(collection, 0) + file_count
                    report.total_files += file_count
                    continue

                batch_report = self._pipeline.ingest_directory(
                    directory=dir_path,
                    patterns=["*.md"],
                    target_collection=collection,
                )
                report.batch_reports.append(batch_report)
                report.total_files += batch_report.total
                report.total_ingested += batch_report.succeeded
                report.total_failed += batch_report.failed
                report.total_skipped += batch_report.skipped

                report.by_collection[collection] = report.by_collection.get(collection, 0) + batch_report.succeeded
                for domain, count in batch_report.by_domain.items():
                    report.by_domain[domain] = report.by_domain.get(domain, 0) + count

        logger.info(
            "docs_population_complete",
            total=report.total_files,
            ingested=report.total_ingested,
            failed=report.total_failed,
        )

        return report

    def populate_from_code_modules(self, dry_run: bool = False) -> PopulationReport:
        """Extract knowledge from existing code modules and populate collections.
        استخراج المعرفة من وحدات الكود الموجودة وتعبئة المجموعات"""
        report = PopulationReport()

        # Map of code modules to collections
        code_sources: list[dict[str, Any]] = [
            {
                "module_path": "shared/yemen/crops.py",
                "description": "Yemen crop data (30+ crops with regions, water needs)",
                "collections": [CROP_KNOWLEDGE, CROP_WATER_REQUIREMENTS],
            },
            {
                "module_path": "shared/yemen/soils.py",
                "description": "Yemen soil profiles",
                "collections": [SOIL_KNOWLEDGE],
            },
            {
                "module_path": "shared/yemen/climate.py",
                "description": "Yemen climate zones (7 zones)",
                "collections": [WEATHER_KNOWLEDGE],
            },
            {
                "module_path": "shared/pest_scouting/identification.py",
                "description": "Pest identification database",
                "collections": [PEST_KNOWLEDGE],
            },
            {
                "module_path": "shared/fertilizer_management/recommendations.py",
                "description": "Crop nutrient requirements",
                "collections": [FERTILIZER_KNOWLEDGE],
            },
            {
                "module_path": "shared/agri_calendar/planting.py",
                "description": "Regional planting windows",
                "collections": [GENERAL_AGRICULTURE],
            },
            {
                "module_path": "shared/irrigation/scheduling.py",
                "description": "Irrigation scheduling algorithms",
                "collections": [IRRIGATION_PRACTICES],
            },
            {
                "module_path": "shared/drone_integration/flight_planning.py",
                "description": "Drone flight planning and VRA",
                "collections": [SMART_AGRICULTURE_KNOWLEDGE],
            },
            {
                "module_path": "shared/smart_agriculture/blockchain.py",
                "description": "Blockchain traceability (23-41% price premium)",
                "collections": [SMART_AGRICULTURE_KNOWLEDGE],
            },
            {
                "module_path": "shared/edge_cloud/cooperative.py",
                "description": "Edge-cloud cooperative architecture",
                "collections": [SMART_AGRICULTURE_KNOWLEDGE],
            },
            {
                "module_path": "shared/ml_irrigation/optimizer.py",
                "description": "ML-based irrigation optimization (70% water savings)",
                "collections": [IRRIGATION_PRACTICES, CROP_WATER_REQUIREMENTS],
            },
            {
                "module_path": "shared/salinity/monitoring.py",
                "description": "Soil salinity monitoring and mitigation",
                "collections": [SOIL_KNOWLEDGE],
            },
            {
                "module_path": "shared/crop_rotation/planner.py",
                "description": "Crop rotation planning for soil health",
                "collections": [CROP_KNOWLEDGE, GENERAL_AGRICULTURE],
            },
        ]

        for source in code_sources:
            module_file = Path(source["module_path"])
            if not module_file.exists():
                logger.debug("code_module_not_found", path=source["module_path"])
                continue

            if dry_run:
                for coll in source["collections"]:
                    report.by_collection[coll] = report.by_collection.get(coll, 0) + 1
                report.total_files += 1
                continue

            # Extract knowledge from code file
            result = self._pipeline.ingest_file(
                file_path=module_file,
                target_collection=source["collections"][0],
                extra_metadata={"source_type": "code_module", "description": source["description"]},
            )

            if result.success:
                report.total_ingested += 1
                for coll in source["collections"]:
                    report.by_collection[coll] = report.by_collection.get(coll, 0) + 1
            else:
                report.total_failed += 1
                report.errors.extend(result.errors)

            report.total_files += 1

        logger.info(
            "code_population_complete",
            total=report.total_files,
            ingested=report.total_ingested,
            failed=report.total_failed,
        )

        return report

    def populate_all(self, dry_run: bool = False) -> PopulationReport:
        """Run full population from both docs and code modules.
        تشغيل التعبئة الكاملة من الوثائق ووحدات الكود"""
        docs_report = self.populate_from_docs(dry_run=dry_run)
        code_report = self.populate_from_code_modules(dry_run=dry_run)

        # Merge reports
        combined = PopulationReport(
            total_files=docs_report.total_files + code_report.total_files,
            total_ingested=docs_report.total_ingested + code_report.total_ingested,
            total_failed=docs_report.total_failed + code_report.total_failed,
            total_skipped=docs_report.total_skipped + code_report.total_skipped,
            errors=docs_report.errors + code_report.errors,
            batch_reports=docs_report.batch_reports,
        )

        # Merge collection counts
        for coll, count in {**docs_report.by_collection, **code_report.by_collection}.items():
            combined.by_collection[coll] = docs_report.by_collection.get(coll, 0) + code_report.by_collection.get(
                coll, 0
            )

        for domain, count in {**docs_report.by_domain, **code_report.by_domain}.items():
            combined.by_domain[domain] = docs_report.by_domain.get(domain, 0) + code_report.by_domain.get(domain, 0)

        logger.info(
            "full_population_complete",
            total=combined.total_files,
            ingested=combined.total_ingested,
            failed=combined.total_failed,
            collections=dict(combined.by_collection),
        )

        return combined

    def get_population_status(self) -> dict[str, Any]:
        """Get current status of all collections (dry run).
        الحصول على حالة جميع المجموعات الحالية"""
        report = self.populate_from_docs(dry_run=True)
        return {
            "collections": {
                coll: {
                    "files_available": report.by_collection.get(coll, 0),
                    "directories": COLLECTION_DIRECTORY_MAP.get(coll, []),
                }
                for coll in ALL_COLLECTIONS
            },
            "total_files": report.total_files,
        }
