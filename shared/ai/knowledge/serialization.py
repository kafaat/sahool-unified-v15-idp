# =============================================================================
# Knowledge Export/Import Serialization (GAP-16)
# تصدير واستيراد وثائق المعرفة
# =============================================================================
#
# Provides JSON (and optionally YAML) serialization for knowledge collections,
# enabling backup, transfer, and API-driven export/import of agricultural
# knowledge documents.
#
# =============================================================================

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any

from shared.ai.knowledge._logging import get_logger

from .models import BaseKnowledgeDocument

logger = get_logger(__name__)


class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that handles date/datetime objects.
    مُشفّر JSON يتعامل مع كائنات التاريخ والوقت"""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)


@dataclass
class ExportManifest:
    """Manifest for an exported knowledge collection.
    بيان لمجموعة معرفة مصدّرة"""

    version: str = "1.0.0"
    exported_at: str = ""
    total_documents: int = 0
    collections: list[str] = field(default_factory=list)
    domains: list[str] = field(default_factory=list)


@dataclass
class ImportResult:
    """Result of importing knowledge documents.
    نتيجة استيراد وثائق المعرفة"""

    total: int = 0
    imported: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)


class KnowledgeSerializer:
    """Export and import knowledge collections as JSON/YAML.
    تصدير واستيراد مجموعات المعرفة بتنسيق JSON/YAML"""

    def export_documents(
        self,
        documents: list[BaseKnowledgeDocument],
        output_path: str | Path,
        format: str = "json",
    ) -> ExportManifest:
        """Export documents to a file.
        تصدير الوثائق إلى ملف"""
        output_path = Path(output_path)

        serialized = [self._serialize_document(doc) for doc in documents]

        domains_set: set[str] = set()
        collections_set: set[str] = set()
        for doc in documents:
            domains_set.add(doc.domain.value)
            collections_set.add(doc._get_collection())

        manifest = ExportManifest(
            version="1.0.0",
            exported_at=datetime.utcnow().isoformat(),
            total_documents=len(serialized),
            collections=sorted(collections_set),
            domains=sorted(domains_set),
        )

        export_payload: dict[str, Any] = {
            "manifest": {
                "version": manifest.version,
                "exported_at": manifest.exported_at,
                "total_documents": manifest.total_documents,
                "collections": manifest.collections,
                "domains": manifest.domains,
            },
            "documents": serialized,
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format == "yaml":
            try:
                import yaml  # type: ignore[import-untyped]

                with open(output_path, "w", encoding="utf-8") as f:
                    yaml.safe_dump(
                        export_payload,
                        f,
                        allow_unicode=True,
                        default_flow_style=False,
                        sort_keys=False,
                    )
            except ImportError:
                logger.warning(
                    "yaml_not_available_falling_back_to_json",
                    message="PyYAML not installed, falling back to JSON",
                )
                output_path = output_path.with_suffix(".json")
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(export_payload, f, cls=DateTimeEncoder, ensure_ascii=False, indent=2)
        else:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(export_payload, f, cls=DateTimeEncoder, ensure_ascii=False, indent=2)

        logger.info(
            "knowledge_exported",
            output_path=str(output_path),
            total_documents=manifest.total_documents,
            format=format,
            domains=manifest.domains,
        )

        return manifest

    def export_to_dict(self, documents: list[BaseKnowledgeDocument]) -> dict[str, Any]:
        """Export documents to a dictionary (for API responses).
        تصدير الوثائق إلى قاموس (لاستجابات API)"""
        serialized = [self._serialize_document(doc) for doc in documents]

        domains_set: set[str] = set()
        collections_set: set[str] = set()
        for doc in documents:
            domains_set.add(doc.domain.value)
            collections_set.add(doc._get_collection())

        return {
            "manifest": {
                "version": "1.0.0",
                "exported_at": datetime.utcnow().isoformat(),
                "total_documents": len(serialized),
                "collections": sorted(collections_set),
                "domains": sorted(domains_set),
            },
            "documents": serialized,
        }

    def import_documents(self, input_path: str | Path) -> tuple[list[BaseKnowledgeDocument], ImportResult]:
        """Import documents from a file. Returns (documents, result).
        استيراد الوثائق من ملف. يُرجع (الوثائق، النتيجة)"""
        input_path = Path(input_path)

        if not input_path.exists():
            logger.error("import_file_not_found", path=str(input_path))
            return [], ImportResult(
                total=0,
                imported=0,
                skipped=0,
                errors=[f"File not found: {input_path}"],
            )

        try:
            raw_text = input_path.read_text(encoding="utf-8")
        except OSError as exc:
            logger.error("import_file_read_error", path=str(input_path), error=str(exc))
            return [], ImportResult(
                total=0,
                imported=0,
                skipped=0,
                errors=[f"Failed to read file: {exc}"],
            )

        suffix = input_path.suffix.lower()
        if suffix in (".yaml", ".yml"):
            try:
                import yaml  # type: ignore[import-untyped]

                data = yaml.safe_load(raw_text)
            except ImportError:
                logger.error("yaml_import_requires_pyyaml")
                return [], ImportResult(
                    total=0,
                    imported=0,
                    skipped=0,
                    errors=["PyYAML is required to import YAML files"],
                )
            except Exception as exc:
                logger.error("yaml_parse_error", error=str(exc))
                return [], ImportResult(
                    total=0,
                    imported=0,
                    skipped=0,
                    errors=[f"YAML parse error: {exc}"],
                )
        else:
            try:
                data = json.loads(raw_text)
            except json.JSONDecodeError as exc:
                logger.error("json_parse_error", path=str(input_path), error=str(exc))
                return [], ImportResult(
                    total=0,
                    imported=0,
                    skipped=0,
                    errors=[f"JSON parse error: {exc}"],
                )

        if not isinstance(data, dict):
            logger.error("import_invalid_format", reason="top-level must be a dict")
            return [], ImportResult(
                total=0, imported=0, skipped=0, errors=["Invalid format: expected a JSON object at top level"]
            )

        return self.import_from_dict(data)

    def import_from_dict(self, data: dict[str, Any]) -> tuple[list[BaseKnowledgeDocument], ImportResult]:
        """Import from a dictionary.
        استيراد من قاموس"""
        raw_documents = data.get("documents", [])
        if not isinstance(raw_documents, list):
            logger.error("import_invalid_documents_field", type=type(raw_documents).__name__)
            return [], ImportResult(
                total=0,
                imported=0,
                skipped=0,
                errors=["'documents' field must be a list"],
            )

        result = ImportResult(total=len(raw_documents))
        documents: list[BaseKnowledgeDocument] = []

        for idx, raw in enumerate(raw_documents):
            if not isinstance(raw, dict):
                result.skipped += 1
                msg = f"Document at index {idx} is not a dict, skipped"
                result.errors.append(msg)
                logger.warning("import_skip_non_dict", index=idx)
                continue

            doc = self._deserialize_document(raw, idx)
            if doc is not None:
                documents.append(doc)
                result.imported += 1
            else:
                result.skipped += 1

        logger.info(
            "knowledge_imported",
            total=result.total,
            imported=result.imported,
            skipped=result.skipped,
            error_count=len(result.errors),
        )

        return documents, result

    def _serialize_document(self, doc: BaseKnowledgeDocument) -> dict[str, Any]:
        """Serialize a single document.
        تسلسل وثيقة واحدة"""
        data = doc.model_dump()
        # Ensure datetime fields are ISO strings for JSON compatibility
        for key, value in data.items():
            if isinstance(value, (datetime, date)):
                data[key] = value.isoformat()
        # Handle nested dicts that may contain date objects
        data = self._convert_dates_recursive(data)
        return data

    def _deserialize_document(self, data: dict[str, Any], index: int = 0) -> BaseKnowledgeDocument | None:
        """Deserialize a single document. Returns None on error.
        إلغاء تسلسل وثيقة واحدة. يُرجع None عند الخطأ"""
        try:
            doc = BaseKnowledgeDocument.model_validate(data)
            return doc
        except Exception as exc:
            doc_id = data.get("id", f"index_{index}")
            logger.warning("import_deserialize_error", document_id=doc_id, error=str(exc))
            return None

    def _convert_dates_recursive(self, obj: Any) -> Any:
        """Recursively convert date/datetime objects to ISO strings.
        تحويل كائنات التاريخ بشكل متكرر إلى سلاسل ISO"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, dict):
            return {k: self._convert_dates_recursive(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._convert_dates_recursive(item) for item in obj]
        return obj
