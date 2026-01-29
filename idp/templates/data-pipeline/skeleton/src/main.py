"""
${{ values.name }} - SAHOOL Data Pipeline
${{ values.description }}
${{ values.description_ar }}

Pipeline Type: ${{ values.pipeline_type }}
Schedule: ${{ values.schedule }}
Input: ${{ values.input_source }}
Output: ${{ values.output_sink }}

Owner: ${{ values.owner }}
Team: ${{ values.team }}
Tier: ${{ values.tier }}
Lifecycle: ${{ values.lifecycle }}

Author: SAHOOL Platform Team
"""

import asyncio
import os
import signal
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, AsyncIterator

import structlog
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, start_http_server

logger = structlog.get_logger()

# ============================================================================
# METRICS
# ============================================================================

RECORDS_PROCESSED = Counter(
    "${{ values.name | snake_case }}_records_processed_total",
    "Total records processed",
    ["status"],
)

PROCESSING_TIME = Histogram(
    "${{ values.name | snake_case }}_processing_seconds",
    "Time spent processing records",
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0],
)

PIPELINE_RUNS = Counter(
    "${{ values.name | snake_case }}_runs_total",
    "Total pipeline runs",
    ["status"],
)


# ============================================================================
# DATA MODELS
# ============================================================================


class PipelineConfig(BaseModel):
    """Pipeline configuration."""

    name: str = "${{ values.name }}"
    pipeline_type: str = "${{ values.pipeline_type }}"
    schedule: str = "${{ values.schedule }}"
    input_source: str = "${{ values.input_source }}"
    output_sink: str = "${{ values.output_sink }}"

    # Connection settings
    nats_url: str = Field(default_factory=lambda: os.getenv("NATS_URL", "nats://nats:4222"))
    database_url: str = Field(default_factory=lambda: os.getenv("DATABASE_URL", ""))
    s3_bucket: str = Field(default_factory=lambda: os.getenv("S3_BUCKET", ""))

    # Processing settings
    batch_size: int = 1000
    max_retries: int = 3
    timeout_seconds: int = 300


class PipelineRecord(BaseModel):
    """Base record model for pipeline."""

    id: str
    data: dict[str, Any]
    source: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class PipelineResult(BaseModel):
    """Result of pipeline processing."""

    success: bool
    records_processed: int
    records_failed: int
    duration_seconds: float
    errors: list[str] = Field(default_factory=list)
    started_at: datetime
    completed_at: datetime


# ============================================================================
# INPUT SOURCES
# ============================================================================


class InputSource:
    """Base class for input sources."""

    async def read(self) -> AsyncIterator[PipelineRecord]:
        """Read records from source."""
        raise NotImplementedError

    async def close(self) -> None:
        """Close the source connection."""
        pass


{%- if values.input_source == "nats" %}
class NATSInputSource(InputSource):
    """NATS input source."""

    def __init__(self, config: PipelineConfig):
        self.config = config
        self._nc = None

    async def connect(self) -> None:
        import nats

        self._nc = await nats.connect(self.config.nats_url)
        logger.info("Connected to NATS", url=self.config.nats_url)

    async def read(self) -> AsyncIterator[PipelineRecord]:
        import json

        sub = await self._nc.subscribe("sahool.${{ values.name | replace('-', '.') }}.>")

        async for msg in sub.messages:
            try:
                data = json.loads(msg.data.decode())
                yield PipelineRecord(
                    id=data.get("id", str(msg.sid)),
                    data=data,
                    source="nats",
                    metadata={"subject": msg.subject},
                )
            except Exception as e:
                logger.error("Failed to parse NATS message", error=str(e))

    async def close(self) -> None:
        if self._nc:
            await self._nc.close()
{%- endif %}

{%- if values.input_source == "postgres" %}
class PostgresInputSource(InputSource):
    """PostgreSQL input source."""

    def __init__(self, config: PipelineConfig):
        self.config = config
        self._pool = None

    async def connect(self) -> None:
        import asyncpg

        self._pool = await asyncpg.create_pool(
            self.config.database_url,
            min_size=2,
            max_size=10,
        )
        logger.info("Connected to PostgreSQL")

    async def read(self) -> AsyncIterator[PipelineRecord]:
        async with self._pool.acquire() as conn:
            # Customize this query for your pipeline
            rows = await conn.fetch(
                """
                SELECT id, data, created_at
                FROM pipeline_input
                WHERE processed = false
                ORDER BY created_at
                LIMIT $1
                """,
                self.config.batch_size,
            )

            for row in rows:
                yield PipelineRecord(
                    id=str(row["id"]),
                    data=row["data"],
                    source="postgres",
                    timestamp=row["created_at"],
                )

    async def close(self) -> None:
        if self._pool:
            await self._pool.close()
{%- endif %}


# ============================================================================
# OUTPUT SINKS
# ============================================================================


class OutputSink:
    """Base class for output sinks."""

    async def write(self, records: list[PipelineRecord]) -> int:
        """Write records to sink. Returns count of written records."""
        raise NotImplementedError

    async def close(self) -> None:
        """Close the sink connection."""
        pass


{%- if values.output_sink == "postgres" %}
class PostgresOutputSink(OutputSink):
    """PostgreSQL output sink."""

    def __init__(self, config: PipelineConfig):
        self.config = config
        self._pool = None

    async def connect(self) -> None:
        import asyncpg

        self._pool = await asyncpg.create_pool(
            self.config.database_url,
            min_size=2,
            max_size=10,
        )
        logger.info("Connected to PostgreSQL (sink)")

    async def write(self, records: list[PipelineRecord]) -> int:
        import json

        async with self._pool.acquire() as conn:
            # Customize this query for your pipeline
            written = 0
            for record in records:
                try:
                    await conn.execute(
                        """
                        INSERT INTO pipeline_output (id, data, source, processed_at)
                        VALUES ($1, $2, $3, $4)
                        ON CONFLICT (id) DO UPDATE SET
                            data = EXCLUDED.data,
                            processed_at = EXCLUDED.processed_at
                        """,
                        record.id,
                        json.dumps(record.data),
                        record.source,
                        datetime.now(timezone.utc),
                    )
                    written += 1
                except Exception as e:
                    logger.error("Failed to write record", id=record.id, error=str(e))

            return written

    async def close(self) -> None:
        if self._pool:
            await self._pool.close()
{%- endif %}

{%- if values.output_sink == "nats" %}
class NATSOutputSink(OutputSink):
    """NATS output sink."""

    def __init__(self, config: PipelineConfig):
        self.config = config
        self._nc = None

    async def connect(self) -> None:
        import nats

        self._nc = await nats.connect(self.config.nats_url)
        logger.info("Connected to NATS (sink)")

    async def write(self, records: list[PipelineRecord]) -> int:
        import json

        written = 0
        for record in records:
            try:
                await self._nc.publish(
                    f"sahool.${{ values.name | replace('-', '.') }}.processed",
                    json.dumps(record.model_dump(), default=str).encode(),
                )
                written += 1
            except Exception as e:
                logger.error("Failed to publish record", id=record.id, error=str(e))

        return written

    async def close(self) -> None:
        if self._nc:
            await self._nc.close()
{%- endif %}


# ============================================================================
# PIPELINE PROCESSOR
# ============================================================================


class Pipeline:
    """
    ${{ values.name }} Pipeline
    ${{ values.description_ar }}

    Processes data from ${{ values.input_source }} to ${{ values.output_sink }}.
    """

    def __init__(self, config: PipelineConfig):
        self.config = config
        self.input_source: InputSource | None = None
        self.output_sink: OutputSink | None = None
        self._running = False

    async def setup(self) -> None:
        """Setup input source and output sink."""
        # Initialize input source
        {%- if values.input_source == "nats" %}
        self.input_source = NATSInputSource(self.config)
        await self.input_source.connect()
        {%- elif values.input_source == "postgres" %}
        self.input_source = PostgresInputSource(self.config)
        await self.input_source.connect()
        {%- endif %}

        # Initialize output sink
        {%- if values.output_sink == "postgres" %}
        self.output_sink = PostgresOutputSink(self.config)
        await self.output_sink.connect()
        {%- elif values.output_sink == "nats" %}
        self.output_sink = NATSOutputSink(self.config)
        await self.output_sink.connect()
        {%- endif %}

        logger.info("Pipeline setup complete")

    async def process_record(self, record: PipelineRecord) -> PipelineRecord:
        """
        Process a single record.
        معالجة سجل واحد

        Override this method to implement your processing logic.
        """
        # TODO: Implement your processing logic here
        # مثال: تحليل البيانات، تحويلها، إثرائها

        # Example transformation
        record.data["processed"] = True
        record.data["processed_at"] = datetime.now(timezone.utc).isoformat()
        record.data["pipeline"] = self.config.name

        return record

    async def validate_record(self, record: PipelineRecord) -> bool:
        """
        Validate a record before processing.
        التحقق من صحة السجل قبل المعالجة
        """
        # TODO: Implement validation logic
        if not record.id:
            return False
        if not record.data:
            return False
        return True

    {%- if values.pipeline_type == "batch" %}
    async def run_batch(self) -> PipelineResult:
        """Run batch processing."""
        started_at = datetime.now(timezone.utc)
        records_processed = 0
        records_failed = 0
        errors = []
        batch = []

        logger.info("Starting batch processing")

        try:
            async for record in self.input_source.read():
                with PROCESSING_TIME.time():
                    try:
                        if not await self.validate_record(record):
                            records_failed += 1
                            RECORDS_PROCESSED.labels(status="invalid").inc()
                            continue

                        processed = await self.process_record(record)
                        batch.append(processed)

                        if len(batch) >= self.config.batch_size:
                            written = await self.output_sink.write(batch)
                            records_processed += written
                            RECORDS_PROCESSED.labels(status="success").inc(written)
                            batch = []

                    except Exception as e:
                        records_failed += 1
                        errors.append(str(e))
                        RECORDS_PROCESSED.labels(status="error").inc()
                        logger.error("Failed to process record", error=str(e))

            # Write remaining batch
            if batch:
                written = await self.output_sink.write(batch)
                records_processed += written

        except Exception as e:
            errors.append(str(e))
            logger.error("Batch processing failed", error=str(e))

        completed_at = datetime.now(timezone.utc)
        duration = (completed_at - started_at).total_seconds()

        result = PipelineResult(
            success=records_failed == 0,
            records_processed=records_processed,
            records_failed=records_failed,
            duration_seconds=duration,
            errors=errors,
            started_at=started_at,
            completed_at=completed_at,
        )

        PIPELINE_RUNS.labels(status="success" if result.success else "failed").inc()
        logger.info(
            "Batch processing complete",
            processed=records_processed,
            failed=records_failed,
            duration=duration,
        )

        return result
    {%- endif %}

    {%- if values.pipeline_type in ["streaming", "hybrid"] %}
    async def run_streaming(self) -> None:
        """Run streaming processing."""
        self._running = True
        logger.info("Starting streaming processing")

        batch = []
        last_flush = datetime.now(timezone.utc)

        try:
            async for record in self.input_source.read():
                if not self._running:
                    break

                with PROCESSING_TIME.time():
                    try:
                        if not await self.validate_record(record):
                            RECORDS_PROCESSED.labels(status="invalid").inc()
                            continue

                        processed = await self.process_record(record)
                        batch.append(processed)
                        RECORDS_PROCESSED.labels(status="success").inc()

                        # Flush batch periodically or when full
                        now = datetime.now(timezone.utc)
                        if (
                            len(batch) >= self.config.batch_size
                            or (now - last_flush).total_seconds() > 10
                        ):
                            await self.output_sink.write(batch)
                            batch = []
                            last_flush = now

                    except Exception as e:
                        RECORDS_PROCESSED.labels(status="error").inc()
                        logger.error("Failed to process record", error=str(e))

        except Exception as e:
            logger.error("Streaming processing failed", error=str(e))

        # Final flush
        if batch:
            await self.output_sink.write(batch)

        logger.info("Streaming processing stopped")

    def stop(self) -> None:
        """Stop streaming processing."""
        self._running = False
    {%- endif %}

    async def cleanup(self) -> None:
        """Cleanup resources."""
        if self.input_source:
            await self.input_source.close()
        if self.output_sink:
            await self.output_sink.close()
        logger.info("Pipeline cleanup complete")


# ============================================================================
# MAIN
# ============================================================================


async def main():
    """Main entry point."""
    # Start metrics server
    metrics_port = int(os.getenv("METRICS_PORT", "9090"))
    start_http_server(metrics_port)
    logger.info("Metrics server started", port=metrics_port)

    # Initialize pipeline
    config = PipelineConfig()
    pipeline = Pipeline(config)

    # Handle shutdown
    def handle_shutdown(sig, frame):
        logger.info("Shutdown signal received")
        {%- if values.pipeline_type in ["streaming", "hybrid"] %}
        pipeline.stop()
        {%- endif %}

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    try:
        await pipeline.setup()

        {%- if values.pipeline_type == "batch" %}
        result = await pipeline.run_batch()
        logger.info("Pipeline result", result=result.model_dump())
        {%- elif values.pipeline_type == "streaming" %}
        await pipeline.run_streaming()
        {%- elif values.pipeline_type == "hybrid" %}
        # Run batch first, then switch to streaming
        result = await pipeline.run_batch()
        logger.info("Batch result", result=result.model_dump())
        await pipeline.run_streaming()
        {%- endif %}

    finally:
        await pipeline.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
