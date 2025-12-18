"""
RAG Utilities - Context building and retrieval helpers
أدوات RAG - بناء السياق ومساعدات الاسترجاع
"""
from typing import List, Dict, Any
from .settings import settings


def build_context(
    hits: List[Dict[str, Any]],
    max_chars: int = None,
    format_template: str = "- ({doc_id}) {text}\n",
) -> str:
    """
    Build context string from search hits for RAG.

    Args:
        hits: List of search hit dictionaries
        max_chars: Maximum characters (default from settings)
        format_template: Format string for each hit

    Returns:
        Formatted context string
    """
    if max_chars is None:
        max_chars = settings.max_context_chars

    chunks = []
    total = 0

    for h in hits:
        piece = format_template.format(
            doc_id=h.get("doc_id", ""),
            text=h.get("text", ""),
            score=h.get("score", 0),
            **h.get("metadata", {}),
        )
        if total + len(piece) > max_chars:
            break
        chunks.append(piece)
        total += len(piece)

    return "".join(chunks).strip()


def build_arabic_context(
    hits: List[Dict[str, Any]],
    max_chars: int = None,
) -> str:
    """
    Build Arabic-formatted context for agricultural advice.

    Args:
        hits: List of search hit dictionaries
        max_chars: Maximum characters

    Returns:
        Arabic formatted context string
    """
    if max_chars is None:
        max_chars = settings.max_context_chars

    chunks = []
    total = 0

    for i, h in enumerate(hits, 1):
        metadata = h.get("metadata", {})
        crop = metadata.get("crop", "")
        region = metadata.get("region", "")

        # Format with Arabic context markers
        header = f"【مصدر {i}】"
        if crop:
            header += f" المحصول: {crop}"
        if region:
            header += f" | المنطقة: {region}"

        piece = f"{header}\n{h.get('text', '')}\n\n"

        if total + len(piece) > max_chars:
            break
        chunks.append(piece)
        total += len(piece)

    return "".join(chunks).strip()


def merge_contexts(
    primary_hits: List[Dict[str, Any]],
    secondary_hits: List[Dict[str, Any]],
    max_chars: int = None,
    primary_weight: float = 0.7,
) -> str:
    """
    Merge contexts from multiple sources with weighting.

    Args:
        primary_hits: Primary search results
        secondary_hits: Secondary/fallback results
        max_chars: Maximum characters
        primary_weight: Proportion of chars for primary (0-1)

    Returns:
        Merged context string
    """
    if max_chars is None:
        max_chars = settings.max_context_chars

    primary_chars = int(max_chars * primary_weight)
    secondary_chars = max_chars - primary_chars

    primary_context = build_context(primary_hits, max_chars=primary_chars)
    secondary_context = build_context(secondary_hits, max_chars=secondary_chars)

    if primary_context and secondary_context:
        return f"{primary_context}\n\n---\n\n{secondary_context}"
    return primary_context or secondary_context


def extract_source_references(hits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extract source references for citation.

    Args:
        hits: List of search hit dictionaries

    Returns:
        List of source reference dictionaries
    """
    refs = []
    for h in hits:
        ref = {
            "doc_id": h.get("doc_id"),
            "score": round(h.get("score", 0), 3),
        }
        metadata = h.get("metadata", {})
        if "title" in metadata:
            ref["title"] = metadata["title"]
        if "source" in metadata:
            ref["source"] = metadata["source"]
        if "date" in metadata:
            ref["date"] = metadata["date"]
        refs.append(ref)
    return refs
