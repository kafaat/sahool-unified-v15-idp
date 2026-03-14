# ═══════════════════════════════════════════════════════════════════════════════
# Knowledge Source Registry
# سجل مصادر المعرفة الزراعية مع تقييم المصداقية
# ═══════════════════════════════════════════════════════════════════════════════
#
# Manages trusted knowledge sources with credibility scoring (1-5):
#   5 = International organizations (FAO, ICARDA, WHO)
#   4 = Government/University (MEWA, agricultural universities)
#   3 = Local research centers (field reports, trials)
#   2 = Specialized agricultural websites (reviewed articles)
#   1 = Community blogs/forums (requires extra verification)
#
# ═══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml
from shared.ai.knowledge._logging import get_logger

from ..models import KnowledgeDomain, SourceCredibilityLevel

logger = get_logger(__name__)

_SOURCES_FILE = Path(__file__).parent / "trusted_sources.yaml"


@dataclass
class TrustedSource:
    """A registered trusted knowledge source | مصدر معرفي موثوق مسجل"""

    name: str
    name_ar: str
    url_patterns: list[str] = field(default_factory=list)
    credibility: SourceCredibilityLevel = SourceCredibilityLevel.SPECIALIZED_WEBSITE
    domains: list[KnowledgeDomain] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    region_coverage: list[str] = field(default_factory=list)
    notes: str = ""


class KnowledgeSourceRegistry:
    """Registry of trusted agricultural knowledge sources with credibility scoring.
    سجل مصادر المعرفة الزراعية الموثوقة مع تقييم المصداقية"""

    def __init__(self, sources_file: Path | None = None) -> None:
        self._sources: list[TrustedSource] = []
        self._sources_file = sources_file or _SOURCES_FILE
        self._loaded = False

    def load(self) -> None:
        """Load trusted sources from YAML configuration."""
        if not self._sources_file.exists():
            logger.warning("trusted_sources_file_not_found", path=str(self._sources_file))
            self._loaded = True
            return

        with open(self._sources_file) as f:
            data = yaml.safe_load(f)

        if not data or "sources" not in data:
            logger.warning("trusted_sources_empty", path=str(self._sources_file))
            self._loaded = True
            return

        for entry in data["sources"]:
            domains = []
            for d in entry.get("domains", []):
                try:
                    domains.append(KnowledgeDomain(d))
                except ValueError:
                    logger.warning(
                        "invalid_domain_in_trusted_source",
                        domain_value=d,
                        source_name=entry.get("name", ""),
                        sources_file=str(self._sources_file),
                    )

            credibility_val = entry.get("credibility", 2)
            try:
                credibility = SourceCredibilityLevel(credibility_val)
            except ValueError:
                credibility = SourceCredibilityLevel.SPECIALIZED_WEBSITE

            source = TrustedSource(
                name=entry.get("name", ""),
                name_ar=entry.get("name_ar", ""),
                url_patterns=entry.get("url_patterns", []),
                credibility=credibility,
                domains=domains,
                languages=entry.get("languages", []),
                region_coverage=entry.get("region_coverage", []),
                notes=entry.get("notes", ""),
            )
            self._sources.append(source)

        self._loaded = True
        logger.info("trusted_sources_loaded", count=len(self._sources))

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            self.load()

    def get_source_credibility(self, url: str) -> SourceCredibilityLevel:
        """Get the credibility level for a URL.
        الحصول على مستوى مصداقية المصدر من الرابط"""
        self._ensure_loaded()
        match = self._find_matching_source(url)
        if match:
            return match.credibility
        return SourceCredibilityLevel.COMMUNITY

    def is_trusted_source(self, url: str, min_credibility: int = 2) -> bool:
        """Check if a URL comes from a trusted source.
        التحقق مما إذا كان الرابط من مصدر موثوق"""
        credibility = self.get_source_credibility(url)
        return credibility.value >= min_credibility

    def get_source_info(self, url: str) -> TrustedSource | None:
        """Get full source information for a URL.
        الحصول على معلومات المصدر الكاملة"""
        self._ensure_loaded()
        return self._find_matching_source(url)

    def get_sources_for_domain(self, domain: KnowledgeDomain) -> list[TrustedSource]:
        """Get all trusted sources relevant to a knowledge domain.
        الحصول على جميع المصادر الموثوقة لمجال معرفي محدد"""
        self._ensure_loaded()
        return [s for s in self._sources if domain in s.domains]

    def get_sources_for_region(self, region: str) -> list[TrustedSource]:
        """Get all trusted sources covering a specific region.
        الحصول على المصادر التي تغطي منطقة محددة"""
        self._ensure_loaded()
        region_lower = region.lower()
        return [
            s
            for s in self._sources
            if any(r.lower() == region_lower or r.lower() == "global" for r in s.region_coverage)
        ]

    def register_source(self, source: TrustedSource) -> None:
        """Register a new trusted source dynamically.
        تسجيل مصدر موثوق جديد"""
        self._ensure_loaded()
        self._sources.append(source)
        logger.info("source_registered", name=source.name, credibility=source.credibility.value)

    def list_all_sources(self) -> list[TrustedSource]:
        """List all registered sources. | عرض جميع المصادر المسجلة"""
        self._ensure_loaded()
        return list(self._sources)

    def to_summary(self) -> dict[str, Any]:
        """Generate a summary of the registry.
        توليد ملخص لسجل المصادر"""
        self._ensure_loaded()
        by_credibility: dict[int, int] = {}
        for s in self._sources:
            by_credibility[s.credibility.value] = by_credibility.get(s.credibility.value, 0) + 1

        return {
            "total_sources": len(self._sources),
            "by_credibility": by_credibility,
            "domains_covered": list({d.value for s in self._sources for d in s.domains}),
            "regions_covered": list({r for s in self._sources for r in s.region_coverage}),
        }

    # ─── Internal ─────────────────────────────────────────────────────────────

    def _find_matching_source(self, url: str) -> TrustedSource | None:
        """Match a URL against registered source patterns."""
        if not url:
            return None

        parsed = urlparse(url)
        hostname = parsed.hostname or ""
        full_url = url.lower()

        for source in self._sources:
            for pattern in source.url_patterns:
                pattern_lower = pattern.lower()
                if pattern_lower in hostname or pattern_lower in full_url:
                    return source
                # Support basic glob patterns
                if "*" in pattern_lower:
                    regex = re.escape(pattern_lower).replace(r"\*", ".*")
                    if re.search(regex, hostname) or re.search(regex, full_url):
                        return source

        return None
