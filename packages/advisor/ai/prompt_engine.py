"""
SAHOOL Prompt Engine
Sprint 9: Template-based prompt rendering

Loads prompt templates from shared/contracts/ai/prompt_templates/
to ensure consistency across the codebase.
"""

from __future__ import annotations

from pathlib import Path

# Root path calculation
ROOT = Path(__file__).resolve().parents[3]
TEMPLATES_DIR = ROOT / "shared" / "contracts" / "ai" / "prompt_templates"
DEFAULT_TEMPLATE = TEMPLATES_DIR / "field_advice_v1.txt"


def get_template(name: str = "field_advice_v1") -> str:
    """Load a prompt template by name.

    Args:
        name: Template name (without .txt extension)

    Returns:
        Template content as string

    Raises:
        FileNotFoundError: If template doesn't exist
    """
    template_path = TEMPLATES_DIR / f"{name}.txt"
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    return template_path.read_text(encoding="utf-8")


def render_prompt(
    *,
    question: str,
    field_context: str,
    retrieved_chunks: str,
    template_name: str = "field_advice_v1",
) -> str:
    """Render a prompt with the given context.

    Args:
        question: User's question
        field_context: Context about the field (NDVI, weather, soil)
        retrieved_chunks: Retrieved knowledge chunks
        template_name: Name of template to use

    Returns:
        Fully rendered prompt ready for LLM
    """
    template = get_template(template_name)
    return (
        template
        .replace("{{question}}", question)
        .replace("{{field_context}}", field_context)
        .replace("{{retrieved_chunks}}", retrieved_chunks)
    )


def list_templates() -> list[str]:
    """List all available prompt templates.

    Returns:
        List of template names (without .txt extension)
    """
    if not TEMPLATES_DIR.exists():
        return []
    return [p.stem for p in TEMPLATES_DIR.glob("*.txt")]
