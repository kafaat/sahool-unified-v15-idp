# ===============================================================================
# Async Knowledge Ingestion Pipeline
# غلاف غير متزامن لخط أنابيب استيعاب المعرفة الزراعية
# ===============================================================================
#
# Wraps the synchronous KnowledgeIngestionPipeline with async interfaces,
# using ThreadPoolExecutor for I/O-bound operations (file reading, extraction).
#
# Reference: GAP-02
# ===============================================================================

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path
from typing import Any

from shared.ai.knowledge._logging import get_logger

from .pipeline import (
    BatchIngestionReport,
    IngestionResult,
    KnowledgeIngestionPipeline,
)

logger = get_logger(__name__)


class AsyncKnowledgeIngestionPipeline:
    """Async wrapper for the knowledge ingestion pipeline.
    غلاف غير متزامن لخط أنابيب استيعاب المعرفة

    Wraps the synchronous KnowledgeIngestionPipeline with async interfaces.
    Uses ThreadPoolExecutor for I/O-bound operations (file reading).

    Usage::

        async with AsyncKnowledgeIngestionPipeline(max_workers=4) as pipeline:
            result = await pipeline.ingest_file("docs/crops/wheat.md")
            report = await pipeline.ingest_files_concurrent(file_list)
    """

    def __init__(
        self,
        pipeline: KnowledgeIngestionPipeline | None = None,
        max_workers: int = 4,
        **pipeline_kwargs: Any,
    ) -> None:
        self._pipeline = pipeline or KnowledgeIngestionPipeline(**pipeline_kwargs)
        self._executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="knowledge-ingestion",
        )

    async def ingest_file(
        self,
        file_path: str | Path,
        source_url: str = "",
        target_collection: str | None = None,
        extra_metadata: dict[str, Any] | None = None,
    ) -> IngestionResult:
        """Async version of ingest_file.
        نسخة غير متزامنة من استيعاب الملف"""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self._executor,
            partial(
                self._pipeline.ingest_file,
                file_path,
                source_url,
                target_collection,
                extra_metadata,
            ),
        )

    async def ingest_text(
        self,
        text: str,
        title: str = "",
        source_url: str = "",
        target_collection: str | None = None,
    ) -> IngestionResult:
        """Async version of ingest_text.
        نسخة غير متزامنة من استيعاب النص"""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self._executor,
            partial(
                self._pipeline.ingest_text,
                text,
                title,
                source_url,
                target_collection,
            ),
        )

    async def ingest_directory(
        self,
        directory: str | Path,
        patterns: list[str] | None = None,
        target_collection: str | None = None,
    ) -> BatchIngestionReport:
        """Async version of ingest_directory.
        نسخة غير متزامنة من استيعاب المجلد"""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self._executor,
            partial(
                self._pipeline.ingest_directory,
                directory,
                patterns,
                target_collection,
            ),
        )

    async def ingest_files_concurrent(
        self,
        file_paths: list[str | Path],
        source_url: str = "",
        target_collection: str | None = None,
        max_concurrent: int = 10,
    ) -> BatchIngestionReport:
        """Ingest multiple files concurrently with semaphore limit.
        استيعاب ملفات متعددة بشكل متزامن مع حد التزامن

        Args:
            file_paths: List of file paths to ingest.
            source_url: Source URL for credibility checking.
            target_collection: Target collection override.
            max_concurrent: Maximum number of concurrent ingestion tasks.

        Returns:
            BatchIngestionReport with aggregated results.
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        report = BatchIngestionReport(total=len(file_paths))

        async def _ingest_one(path: str | Path) -> IngestionResult:
            async with semaphore:
                return await self.ingest_file(path, source_url, target_collection)

        tasks = [_ingest_one(p) for p in file_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for r in results:
            if isinstance(r, Exception):
                report.failed += 1
                report.results.append(IngestionResult(errors=[str(r)]))
            else:
                report.results.append(r)
                if r.success:
                    report.succeeded += 1
                    report.by_collection[r.collection] = report.by_collection.get(r.collection, 0) + 1
                    for d in r.domains_detected:
                        report.by_domain[d] = report.by_domain.get(d, 0) + 1
                else:
                    report.failed += 1

        report.skipped = report.total - report.succeeded - report.failed

        logger.info(
            "async_batch_ingestion_complete",
            total=report.total,
            succeeded=report.succeeded,
            failed=report.failed,
        )

        return report

    async def close(self) -> None:
        """Shutdown the thread pool executor.
        إيقاف مجمع مؤشرات الترابط"""
        self._executor.shutdown(wait=False)

    async def __aenter__(self) -> AsyncKnowledgeIngestionPipeline:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
