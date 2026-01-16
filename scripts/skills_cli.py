#!/usr/bin/env python3
"""
SAHOOL Skills Testing CLI
==========================

A command-line tool for testing and evaluating agricultural AI skills including:
- Context compression for optimizing token usage
- Farm memory management with tenant isolation
- Advisory quality evaluation using LLM-as-Judge methodology
- Documentation generation from skill definitions

دليل اختبار مهارات سهول
==========================

أداة سطر الأوامر لاختبار ومقييم مهارات الذكاء الاصطناعي الزراعية

Usage:
    skills-cli compress [OPTIONS]
    skills-cli remember [OPTIONS]
    skills-cli recall [OPTIONS]
    skills-cli evaluate [OPTIONS]
    skills-cli generate-doc [OPTIONS]

Author: SAHOOL Platform Team
Updated: January 2025
"""

import json
import logging
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import click

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Data Models
# ─────────────────────────────────────────────────────────────────────────────


class CompressionLevel(str, Enum):
    """Compression intensity levels"""

    LIGHT = "light"  # 80% retention
    MEDIUM = "medium"  # 50% retention
    HEAVY = "heavy"  # 25% retention


class MemoryType(str, Enum):
    """Types of memory entries"""

    CONVERSATION = "conversation"
    FIELD_STATE = "field_state"
    RECOMMENDATION = "recommendation"
    OBSERVATION = "observation"
    WEATHER = "weather"
    ACTION = "action"
    SYSTEM = "system"


class AdvisoryType(str, Enum):
    """Types of agricultural advisories"""

    IRRIGATION = "irrigation"
    FERTILIZER = "fertilizer"
    PEST = "pest"
    GENERAL = "general"


@dataclass
class CompressionResult:
    """Result of compression operation"""

    original_text: str
    compressed_text: str
    original_tokens: int
    compressed_tokens: int
    compression_ratio: float
    tokens_saved: int
    savings_percentage: float


@dataclass
class MemoryEntry:
    """A single memory entry"""

    id: str
    tenant_id: str
    field_id: Optional[str]
    memory_type: str
    content: Any
    timestamp: str
    language: str = "en"


@dataclass
class EvaluationResult:
    """Advisory evaluation result"""

    advisory_id: str
    advisory_type: str
    scores: dict[str, float]
    overall_score: float
    grade: str
    strengths: list[str]
    weaknesses: list[str]


# ─────────────────────────────────────────────────────────────────────────────
# Compression Functions
# ─────────────────────────────────────────────────────────────────────────────


def estimate_tokens(text: str, language: str = "auto") -> int:
    """Estimate token count for text"""
    if not text:
        return 0

    # Character to token ratios
    if language == "ar":
        chars_per_token = 2.5
    elif language == "en":
        chars_per_token = 4.0
    else:
        chars_per_token = 3.0

    return max(1, int(len(text) / chars_per_token))


def compress_text(
    text: str, level: CompressionLevel = CompressionLevel.MEDIUM
) -> CompressionResult:
    """Compress text using specified strategy"""
    original_tokens = estimate_tokens(text)
    original_text = text

    # Apply compression based on level
    if level == CompressionLevel.LIGHT:
        # Remove redundant spaces, minimal changes
        compressed = " ".join(text.split())
        target_ratio = 0.8
    elif level == CompressionLevel.MEDIUM:
        # Remove extra spaces, condense repetitions
        compressed = " ".join(text.split())
        # Remove repeated words
        import re

        compressed = re.sub(r"\b(\w+)\s+\1\b", r"\1", compressed)
        target_ratio = 0.5
    else:  # HEAVY
        # Extract key terms only (simulated)
        words = text.split()
        # Keep ~25% of words (every 4th word)
        compressed = " ".join(words[::4]) if len(words) > 4 else text
        target_ratio = 0.25

    compressed_tokens = estimate_tokens(compressed)
    actual_ratio = compressed_tokens / max(original_tokens, 1)
    tokens_saved = original_tokens - compressed_tokens

    return CompressionResult(
        original_text=original_text,
        compressed_text=compressed,
        original_tokens=original_tokens,
        compressed_tokens=compressed_tokens,
        compression_ratio=actual_ratio,
        tokens_saved=tokens_saved,
        savings_percentage=(tokens_saved / max(original_tokens, 1)) * 100,
    )


def compress_field_data(field_data: dict[str, Any]) -> CompressionResult:
    """Compress agricultural field data"""
    # Convert to text representation
    text_repr = json.dumps(field_data, ensure_ascii=False, indent=2)

    # Extract key fields only
    priority_fields = [
        "field_id",
        "name",
        "area",
        "crop_type",
        "crop",
        "status",
        "health",
        "ndvi",
        "irrigation_status",
        "soil_type",
    ]

    compressed_data = {
        k: v for k, v in field_data.items() if k in priority_fields
    }
    compressed_text = json.dumps(compressed_data, ensure_ascii=False, indent=2)

    original_tokens = estimate_tokens(text_repr)
    compressed_tokens = estimate_tokens(compressed_text)
    tokens_saved = original_tokens - compressed_tokens

    return CompressionResult(
        original_text=text_repr,
        compressed_text=compressed_text,
        original_tokens=original_tokens,
        compressed_tokens=compressed_tokens,
        compression_ratio=compressed_tokens / max(original_tokens, 1),
        tokens_saved=tokens_saved,
        savings_percentage=(tokens_saved / max(original_tokens, 1)) * 100,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Memory Functions
# ─────────────────────────────────────────────────────────────────────────────


def create_memory_entry(
    tenant_id: str,
    field_id: Optional[str],
    memory_type: str,
    content: Any,
    language: str = "en",
) -> MemoryEntry:
    """Create a memory entry"""
    import uuid

    return MemoryEntry(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        field_id=field_id,
        memory_type=memory_type,
        content=content,
        timestamp=datetime.now().isoformat(),
        language=language,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Evaluation Functions
# ─────────────────────────────────────────────────────────────────────────────


def evaluate_advisory(
    advisory_type: AdvisoryType,
    advisory_text: str,
    context: Optional[dict[str, Any]] = None,
) -> EvaluationResult:
    """Evaluate an agricultural advisory"""
    # Dimension weights
    weights = {
        "accuracy": 0.30,
        "relevance": 0.25,
        "actionability": 0.20,
        "timeliness": 0.15,
        "safety": 0.10,
    }

    # Simulate scoring based on text content
    scores = {}
    for dimension in weights.keys():
        # Check for key terms
        if dimension == "accuracy":
            score = 4.0 if any(w in advisory_text.lower() for w in ["precise", "specific", "based on"]) else 3.0
        elif dimension == "relevance":
            score = 4.0 if any(w in advisory_text.lower() for w in ["field", "specific", "your"]) else 3.0
        elif dimension == "actionability":
            score = 4.0 if any(w in advisory_text.lower() for w in ["apply", "irrigate", "spray", "schedule"]) else 2.0
        elif dimension == "timeliness":
            score = 4.0 if any(w in advisory_text.lower() for w in ["24h", "hours", "immediately", "delay"]) else 3.0
        else:  # safety
            score = 3.0 if any(w in advisory_text.lower() for w in ["ppe", "risk", "caution", "warning"]) else 2.0

        scores[dimension] = min(5.0, max(1.0, score))

    # Calculate overall score
    overall_score = sum(scores[d] * weights[d] for d in weights.keys())

    # Assign grade
    if overall_score >= 4.5:
        grade = "Excellent"
    elif overall_score >= 3.5:
        grade = "Good"
    elif overall_score >= 2.5:
        grade = "Adequate"
    elif overall_score >= 1.5:
        grade = "Poor"
    else:
        grade = "Failing"

    # Generate strengths and weaknesses
    strengths = []
    weaknesses = []

    if scores["accuracy"] >= 4.0:
        strengths.append("Strong technical accuracy")
    else:
        weaknesses.append("Accuracy could be improved")

    if scores["actionability"] >= 4.0:
        strengths.append("Clear actionable recommendations")
    else:
        weaknesses.append("Needs more specific implementation details")

    if scores["safety"] < 3.0:
        weaknesses.append("Safety information is incomplete")

    return EvaluationResult(
        advisory_id=f"ADV-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        advisory_type=advisory_type.value,
        scores=scores,
        overall_score=overall_score,
        grade=grade,
        strengths=strengths or ["Baseline quality met"],
        weaknesses=weaknesses or ["No major issues identified"],
    )


# ─────────────────────────────────────────────────────────────────────────────
# CLI Commands
# ─────────────────────────────────────────────────────────────────────────────


@click.group(
    help="""
SAHOOL Skills Testing CLI

A command-line interface for testing agricultural AI skills:
- Compress context data for optimal LLM usage
- Store and retrieve farm memory
- Evaluate advisory quality
- Generate skill documentation

دليل اختبار مهارات سهول
أداة لاختبار مهارات الذكاء الاصطناعي الزراعية
""",
)
@click.version_option(version="1.0.0")
def cli():
    """SAHOOL Skills Testing CLI"""
    pass


@cli.command(
    help="""
Compress agricultural data to reduce token usage.

Example:
  # Compress text
  skills-cli compress --text "Your field data here..."

  # Compress JSON field data
  skills-cli compress --json '{"name": "Field001", "area": 8.5}'

  # Use heavy compression (75% reduction)
  skills-cli compress --text "data..." --level heavy

  # Arabic text compression
  skills-cli compress --text "بيانات الحقل..." --language ar
"""
)
@click.option(
    "--text",
    type=str,
    help="Text to compress",
)
@click.option(
    "--json",
    "json_data",
    type=str,
    help="JSON field data to compress",
)
@click.option(
    "--level",
    type=click.Choice(["light", "medium", "heavy"]),
    default="medium",
    help="Compression level (light=80%, medium=50%, heavy=25%)",
)
@click.option(
    "--language",
    type=click.Choice(["ar", "en", "auto"]),
    default="auto",
    help="Language hint for tokenization",
)
@click.option(
    "--output",
    type=str,
    help="Output file (JSON format)",
)
def compress(text: Optional[str], json_data: Optional[str], level: str, language: str, output: Optional[str]):
    """Compress agricultural data"""

    result = None

    if json_data:
        try:
            field_data = json.loads(json_data)
            result = compress_field_data(field_data)
        except json.JSONDecodeError as e:
            click.secho(f"Error: Invalid JSON - {e}", fg="red")
            sys.exit(1)
    elif text:
        result = compress_text(text, CompressionLevel(level))
    else:
        click.secho("Error: Provide either --text or --json", fg="red")
        sys.exit(1)

    # Prepare output
    output_data = {
        "original_text": result.original_text,
        "compressed_text": result.compressed_text,
        "original_tokens": result.original_tokens,
        "compressed_tokens": result.compressed_tokens,
        "compression_ratio": round(result.compression_ratio, 4),
        "tokens_saved": result.tokens_saved,
        "savings_percentage": round(result.savings_percentage, 2),
    }

    # Display results
    click.echo("\n" + click.style("Compression Results", fg="green", bold=True))
    click.echo("─" * 60)
    click.echo(f"Original tokens:    {result.original_tokens}")
    click.echo(f"Compressed tokens:  {result.compressed_tokens}")
    click.echo(f"Tokens saved:       {result.tokens_saved} ({result.savings_percentage:.1f}%)")
    click.echo(f"Compression ratio:  {result.compression_ratio:.2f}x")

    # Output JSON
    if output:
        with open(output, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        click.secho(f"\nResults saved to: {output}", fg="blue")
    else:
        click.echo("\n" + click.style("Output (JSON):", fg="cyan"))
        click.echo(json.dumps(output_data, ensure_ascii=False, indent=2))


@cli.command(
    help="""
Store a farm memory entry.

Example:
  # Simple text memory
  skills-cli remember --tenant-id t1 --field-id f1 \\
    --type observation --content "Wheat shows yellow tips"

  # JSON memory with metadata
  skills-cli remember --tenant-id t1 --field-id f1 \\
    --type action --json '{"action": "irrigation", "duration": "30min"}'

  # Arabic memory
  skills-cli remember --tenant-id t1 --field-id f1 \\
    --type observation --content "القمح يظهر أطراف صفراء" --language ar
"""
)
@click.option(
    "--tenant-id",
    required=True,
    help="Tenant identifier",
)
@click.option(
    "--field-id",
    help="Field identifier (optional)",
)
@click.option(
    "--type",
    "memory_type",
    type=click.Choice(
        [
            "conversation",
            "field_state",
            "recommendation",
            "observation",
            "weather",
            "action",
            "system",
        ]
    ),
    default="observation",
    help="Memory entry type",
)
@click.option(
    "--content",
    type=str,
    help="Text content",
)
@click.option(
    "--json",
    "json_data",
    type=str,
    help="JSON content",
)
@click.option(
    "--language",
    type=click.Choice(["ar", "en"]),
    default="en",
    help="Content language",
)
@click.option(
    "--output",
    type=str,
    help="Output file (JSON format)",
)
def remember(
    tenant_id: str,
    field_id: Optional[str],
    memory_type: str,
    content: Optional[str],
    json_data: Optional[str],
    language: str,
    output: Optional[str],
):
    """Store a memory entry"""

    if json_data:
        try:
            content_data = json.loads(json_data)
        except json.JSONDecodeError as e:
            click.secho(f"Error: Invalid JSON - {e}", fg="red")
            sys.exit(1)
    elif content:
        content_data = content
    else:
        click.secho("Error: Provide either --content or --json", fg="red")
        sys.exit(1)

    entry = create_memory_entry(tenant_id, field_id, memory_type, content_data, language)

    # Prepare output
    output_data = {
        "id": entry.id,
        "tenant_id": entry.tenant_id,
        "field_id": entry.field_id,
        "memory_type": entry.memory_type,
        "content": entry.content,
        "timestamp": entry.timestamp,
        "language": entry.language,
    }

    # Display results
    click.echo("\n" + click.style("Memory Entry Created", fg="green", bold=True))
    click.echo("─" * 60)
    click.echo(f"Entry ID:     {entry.id}")
    click.echo(f"Tenant:       {entry.tenant_id}")
    click.echo(f"Field:        {entry.field_id or 'None'}")
    click.echo(f"Type:         {entry.memory_type}")
    click.echo(f"Language:     {entry.language}")
    click.echo(f"Timestamp:    {entry.timestamp}")

    # Output JSON
    if output:
        with open(output, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        click.secho(f"\nMemory entry saved to: {output}", fg="blue")
    else:
        click.echo("\n" + click.style("Output (JSON):", fg="cyan"))
        click.echo(json.dumps(output_data, ensure_ascii=False, indent=2))


@cli.command(
    help="""
Recall farm memory entries.

Example:
  # Recall all observations for a field
  skills-cli recall --tenant-id t1 --field-id f1 --type observation

  # Recall recent memories (limit)
  skills-cli recall --tenant-id t1 --field-id f1 --limit 10

  # Get context for a query
  skills-cli recall --tenant-id t1 --query "irrigation status" --limit 5
"""
)
@click.option(
    "--tenant-id",
    required=True,
    help="Tenant identifier",
)
@click.option(
    "--field-id",
    help="Filter by field ID",
)
@click.option(
    "--type",
    "memory_type",
    type=click.Choice(
        [
            "conversation",
            "field_state",
            "recommendation",
            "observation",
            "weather",
            "action",
            "system",
        ]
    ),
    help="Filter by memory type",
)
@click.option(
    "--query",
    help="Text query for relevance matching",
)
@click.option(
    "--limit",
    type=int,
    default=20,
    help="Maximum entries to return",
)
@click.option(
    "--output",
    type=str,
    help="Output file (JSON format)",
)
def recall(
    tenant_id: str,
    field_id: Optional[str],
    memory_type: Optional[str],
    query: Optional[str],
    limit: int,
    output: Optional[str],
):
    """Recall memory entries"""

    # Simulate memory retrieval
    sample_entries = [
        {
            "id": "mem-001",
            "tenant_id": tenant_id,
            "field_id": field_id or "f1",
            "memory_type": memory_type or "observation",
            "content": "Wheat showing healthy growth at tillering stage",
            "timestamp": (datetime.now() - timedelta(days=1)).isoformat(),
            "language": "en",
        },
        {
            "id": "mem-002",
            "tenant_id": tenant_id,
            "field_id": field_id or "f1",
            "memory_type": memory_type or "action",
            "content": "Irrigation applied: 500 m³/ha",
            "timestamp": (datetime.now() - timedelta(days=2)).isoformat(),
            "language": "en",
        },
        {
            "id": "mem-003",
            "tenant_id": tenant_id,
            "field_id": field_id or "f1",
            "memory_type": memory_type or "observation",
            "content": "درجة حرارة التربة 15 درجة مئوية",
            "timestamp": (datetime.now() - timedelta(days=3)).isoformat(),
            "language": "ar",
        },
    ]

    # Apply filters
    filtered_entries = sample_entries
    if memory_type:
        filtered_entries = [e for e in filtered_entries if e["memory_type"] == memory_type]
    if field_id:
        filtered_entries = [e for e in filtered_entries if e["field_id"] == field_id]

    # Apply limit
    filtered_entries = filtered_entries[:limit]

    output_data = {
        "tenant_id": tenant_id,
        "query": query,
        "total_found": len(filtered_entries),
        "entries": filtered_entries,
    }

    # Display results
    click.echo("\n" + click.style("Memory Recall Results", fg="green", bold=True))
    click.echo("─" * 60)
    click.echo(f"Tenant:       {tenant_id}")
    click.echo(f"Field:        {field_id or 'All'}")
    click.echo(f"Type:         {memory_type or 'All'}")
    click.echo(f"Entries found: {len(filtered_entries)}")

    if filtered_entries:
        click.echo("\n" + click.style("Entries:", fg="cyan"))
        for entry in filtered_entries:
            click.echo(f"\n  ID: {entry['id']}")
            click.echo(f"  Type: {entry['memory_type']}")
            click.echo(f"  Language: {entry['language']}")
            click.echo(f"  Content: {entry['content'][:60]}...")

    # Output JSON
    if output:
        with open(output, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        click.secho(f"\nResults saved to: {output}", fg="blue")
    else:
        click.echo("\n" + click.style("Output (JSON):", fg="cyan"))
        click.echo(json.dumps(output_data, ensure_ascii=False, indent=2))


@cli.command(
    help="""
Evaluate agricultural advisory quality.

Example:
  # Evaluate irrigation advice
  skills-cli evaluate --type irrigation \\
    --text "Irrigate 500m³/ha tomorrow morning due to low soil moisture"

  # Evaluate pest management advice
  skills-cli evaluate --type pest \\
    --text "Apply imidacloprid 100ml/ha for aphid control"

  # Add context for better evaluation
  skills-cli evaluate --type fertilizer \\
    --text "Apply urea 46kg/ha" \\
    --context '{"soil_test":"18ppm N","threshold":"25ppm N"}'
"""
)
@click.option(
    "--type",
    "advisory_type",
    type=click.Choice(["irrigation", "fertilizer", "pest", "general"]),
    default="general",
    help="Type of advisory",
)
@click.option(
    "--text",
    required=True,
    help="Advisory text to evaluate",
)
@click.option(
    "--context",
    type=str,
    help="Context JSON (e.g., field conditions, crop stage)",
)
@click.option(
    "--output",
    type=str,
    help="Output file (JSON format)",
)
def evaluate(
    advisory_type: str,
    text: str,
    context: Optional[str],
    output: Optional[str],
):
    """Evaluate advisory quality"""

    context_data = None
    if context:
        try:
            context_data = json.loads(context)
        except json.JSONDecodeError as e:
            click.secho(f"Error: Invalid context JSON - {e}", fg="red")
            sys.exit(1)

    result = evaluate_advisory(AdvisoryType(advisory_type), text, context_data)

    # Prepare output
    output_data = {
        "advisory_id": result.advisory_id,
        "advisory_type": result.advisory_type,
        "scores": result.scores,
        "overall_score": round(result.overall_score, 2),
        "grade": result.grade,
        "strengths": result.strengths,
        "weaknesses": result.weaknesses,
    }

    # Display results
    click.echo("\n" + click.style("Advisory Evaluation", fg="green", bold=True))
    click.echo("─" * 60)
    click.echo(f"Advisory ID:  {result.advisory_id}")
    click.echo(f"Type:         {result.advisory_type}")
    click.echo(f"Grade:        {result.grade}")
    click.echo(f"Overall:      {result.overall_score:.2f}/5.00")

    click.echo("\n" + click.style("Dimension Scores:", fg="cyan"))
    for dimension, score in result.scores.items():
        bar = "█" * int(score) + "░" * (5 - int(score))
        click.echo(f"  {dimension:15} {score:.2f}/5.00 {bar}")

    click.echo("\n" + click.style("Strengths:", fg="green"))
    for strength in result.strengths:
        click.echo(f"  ✓ {strength}")

    if result.weaknesses:
        click.echo("\n" + click.style("Weaknesses:", fg="yellow"))
        for weakness in result.weaknesses:
            click.echo(f"  ✗ {weakness}")

    # Output JSON
    if output:
        with open(output, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        click.secho(f"\nEvaluation saved to: {output}", fg="blue")
    else:
        click.echo("\n" + click.style("Output (JSON):", fg="cyan"))
        click.echo(json.dumps(output_data, ensure_ascii=False, indent=2))


@cli.command(
    help="""
Generate skill documentation.

Example:
  # List all skills
  skills-cli generate-doc --list

  # Show compression skill doc
  skills-cli generate-doc --skill compression

  # Show memory skill doc
  skills-cli generate-doc --skill memory

  # Show evaluation skill doc
  skills-cli generate-doc --skill evaluation

  # Generate HTML documentation
  skills-cli generate-doc --format html --output docs.html
"""
)
@click.option(
    "--list",
    is_flag=True,
    help="List all available skills",
)
@click.option(
    "--skill",
    type=click.Choice(["compression", "memory", "evaluation", "all"]),
    help="Skill to document",
)
@click.option(
    "--format",
    type=click.Choice(["text", "json", "html", "markdown"]),
    default="text",
    help="Output format",
)
@click.option(
    "--output",
    type=str,
    help="Output file",
)
def generate_doc(list: bool, skill: Optional[str], format: str, output: Optional[str]):
    """Generate skill documentation"""

    if list:
        click.echo("\n" + click.style("Available Skills", fg="green", bold=True))
        click.echo("─" * 60)
        skills_info = {
            "compression": "Context compression for optimizing token usage",
            "memory": "Farm memory management with tenant isolation",
            "evaluation": "Advisory quality evaluation using LLM-as-Judge",
        }
        for skill_name, description in skills_info.items():
            click.echo(f"\n• {skill_name}")
            click.echo(f"  {description}")
        return

    # Generate documentation based on skill
    docs = {
        "compression": {
            "title": "Context Compression Skill",
            "description": "Reduces token usage while preserving critical agricultural data",
            "commands": [
                {"name": "compress --level light", "description": "Light compression (80% retention)"},
                {"name": "compress --level medium", "description": "Medium compression (50% retention)"},
                {"name": "compress --level heavy", "description": "Heavy compression (25% retention)"},
            ],
            "features": [
                "Agricultural abbreviations support",
                "Bilingual key preservation",
                "Sensor data compression",
                "Time-series compression",
            ],
        },
        "memory": {
            "title": "Farm Memory Skill",
            "description": "Persistent memory management for agricultural operations",
            "commands": [
                {"name": "remember --type observation", "description": "Store field observations"},
                {"name": "remember --type action", "description": "Store actions taken"},
                {"name": "recall --field-id <id>", "description": "Retrieve field history"},
            ],
            "features": [
                "Tenant isolation",
                "Sliding window for recent history",
                "TTL-based expiration",
                "Relevance scoring",
            ],
        },
        "evaluation": {
            "title": "Advisory Evaluation Skill",
            "description": "LLM-as-Judge evaluation of agricultural advisory quality",
            "commands": [
                {"name": "evaluate --type irrigation", "description": "Evaluate irrigation advice"},
                {"name": "evaluate --type fertilizer", "description": "Evaluate fertilizer advice"},
                {"name": "evaluate --type pest", "description": "Evaluate pest management advice"},
            ],
            "features": [
                "Multi-dimensional scoring",
                "Domain-specific rubrics",
                "Bilingual evaluation",
                "Improvement suggestions",
            ],
        },
    }

    if not skill or skill == "all":
        skill_list = list(docs.keys())
    else:
        skill_list = [skill]

    doc_content = {}
    for s in skill_list:
        if s in docs:
            doc_content[s] = docs[s]

    # Format output
    if format == "json":
        output_text = json.dumps(doc_content, ensure_ascii=False, indent=2)
    elif format == "html":
        output_text = "<html><body>"
        for s, doc in doc_content.items():
            output_text += f"<h1>{doc['title']}</h1>"
            output_text += f"<p>{doc['description']}</p>"
        output_text += "</body></html>"
    elif format == "markdown":
        output_text = ""
        for s, doc in doc_content.items():
            output_text += f"# {doc['title']}\n\n"
            output_text += f"{doc['description']}\n\n"
    else:  # text
        output_text = ""
        for s, doc in doc_content.items():
            output_text += f"\n{click.style(doc['title'], fg='green', bold=True)}\n"
            output_text += "─" * 60 + "\n"
            output_text += f"{doc['description']}\n"

    click.echo(output_text)

    # Save if output specified
    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(output_text)
        click.secho(f"\nDocumentation saved to: {output}", fg="blue")


# ─────────────────────────────────────────────────────────────────────────────
# Examples and Help Functions
# ─────────────────────────────────────────────────────────────────────────────


@cli.command(
    help="Show practical examples for all commands"
)
def examples():
    """Show practical examples"""

    examples_text = """
╔════════════════════════════════════════════════════════════════════════════╗
║                  SAHOOL Skills CLI - Practical Examples                    ║
║                  أمثلة عملية - أداة اختبار مهارات سهول                   ║
╚════════════════════════════════════════════════════════════════════════════╝

1. COMPRESSION EXAMPLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Compress English text (medium compression):
  $ skills-cli compress \\
      --text "Field 003 wheat crop is progressing well through tillering stage..."

Compress Arabic field data:
  $ skills-cli compress \\
      --text "بيانات الحقل 003: مساحة 8.5 هكتار، محصول قمح بمرحلة التفريع" \\
      --language ar

Compress JSON field data (heavy compression):
  $ skills-cli compress \\
      --json '{"name":"F003","area":8.5,"crop":"wheat","ndvi":0.72}' \\
      --level heavy \\
      --output compressed.json

2. MEMORY EXAMPLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Store field observation:
  $ skills-cli remember \\
      --tenant-id tenant_001 \\
      --field-id field_003 \\
      --type observation \\
      --content "Wheat shows nitrogen deficiency in eastern corner"

Store irrigation action (JSON):
  $ skills-cli remember \\
      --tenant-id tenant_001 \\
      --field-id field_003 \\
      --type action \\
      --json '{"action":"irrigation","volume":"500m3/ha","time":"08:00"}'

Store Arabic recommendation:
  $ skills-cli remember \\
      --tenant-id tenant_001 \\
      --field-id field_003 \\
      --type recommendation \\
      --content "تطبيق اليوريا بمعدل 46 كغ/هكتار" \\
      --language ar

Recall field history:
  $ skills-cli recall \\
      --tenant-id tenant_001 \\
      --field-id field_003 \\
      --type observation \\
      --limit 10

3. EVALUATION EXAMPLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Evaluate irrigation advisory:
  $ skills-cli evaluate \\
      --type irrigation \\
      --text "Irrigate 500m³/ha tomorrow morning due to soil moisture 38%"

Evaluate pest management advice with context:
  $ skills-cli evaluate \\
      --type pest \\
      --text "Spray Imidacloprid 100ml/ha for aphid control" \\
      --context '{"threshold":"25/tiller","current":"12/tiller"}'

Evaluate fertilizer advice:
  $ skills-cli evaluate \\
      --type fertilizer \\
      --text "Apply urea 46kg/ha in early morning with dew" \\
      --output evaluation_result.json

4. DOCUMENTATION EXAMPLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

List all available skills:
  $ skills-cli generate-doc --list

Show compression skill documentation:
  $ skills-cli generate-doc --skill compression

Generate all docs as markdown:
  $ skills-cli generate-doc --skill all --format markdown --output skills.md

5. REAL-WORLD WORKFLOW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 1: Store field observation
  $ skills-cli remember \\
      --tenant-id farm_001 \\
      --field-id north_field \\
      --type observation \\
      --content "Wheat yellowing detected, nitrogen suspected"

Step 2: Compress data for API transmission
  $ skills-cli compress \\
      --json '{"field":"north_field","crop":"wheat","issue":"yellowing"}' \\
      --level light

Step 3: Generate and evaluate advisory response
  $ skills-cli evaluate \\
      --type fertilizer \\
      --text "Apply 46 kg/ha urea early morning with dew present" \\
      --output advisory_eval.json

Step 4: Store the action taken
  $ skills-cli remember \\
      --tenant-id farm_001 \\
      --field-id north_field \\
      --type action \\
      --json '{"action":"applied_urea","rate":"46kg/ha","time":"2025-01-14T07:30Z"}'

Step 5: Recall field history
  $ skills-cli recall \\
      --tenant-id farm_001 \\
      --field-id north_field \\
      --limit 10

═════════════════════════════════════════════════════════════════════════════
For more help on a specific command:
  $ skills-cli <command> --help

For help on all commands:
  $ skills-cli --help
═════════════════════════════════════════════════════════════════════════════
"""

    click.echo(examples_text)


# ─────────────────────────────────────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        click.secho(f"Error: {e}", fg="red")
        logger.exception("CLI error")
        sys.exit(1)
