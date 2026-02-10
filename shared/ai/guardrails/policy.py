"""
Guard Policy Management
إدارة سياسات الحماية

JSON-based policy configuration for guardrails.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, UTC
from pathlib import Path
from typing import Any


@dataclass
class PolicyRule:
    """Single policy rule | قاعدة سياسة واحدة"""

    id: str
    name: str
    name_ar: str
    type: str  # "allow", "deny", "limit"
    target: str  # Tool pattern or domain
    conditions: dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    priority: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "name_ar": self.name_ar,
            "type": self.type,
            "target": self.target,
            "conditions": self.conditions,
            "enabled": self.enabled,
            "priority": self.priority,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PolicyRule:
        return cls(
            id=data["id"],
            name=data["name"],
            name_ar=data.get("name_ar", ""),
            type=data["type"],
            target=data["target"],
            conditions=data.get("conditions", {}),
            enabled=data.get("enabled", True),
            priority=data.get("priority", 0),
        )


@dataclass
class GuardPolicy:
    """
    Complete guard policy configuration.
    تكوين سياسة الحماية الكاملة
    """

    version: str = "1.0"
    name: str = "default"
    name_ar: str = "افتراضي"
    description: str = ""
    description_ar: str = ""
    enabled: bool = True
    rules: list[PolicyRule] = field(default_factory=list)
    tool_allowlist: list[str] = field(default_factory=list)
    domain_allowlist: list[str] = field(default_factory=list)
    blocked_patterns: list[str] = field(default_factory=list)
    dangerous_commands: list[str] = field(default_factory=list)
    limits: dict[str, int] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "name": self.name,
            "name_ar": self.name_ar,
            "description": self.description,
            "description_ar": self.description_ar,
            "enabled": self.enabled,
            "rules": [r.to_dict() for r in self.rules],
            "tool_allowlist": self.tool_allowlist,
            "domain_allowlist": self.domain_allowlist,
            "blocked_patterns": self.blocked_patterns,
            "dangerous_commands": self.dangerous_commands,
            "limits": self.limits,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GuardPolicy:
        rules = [PolicyRule.from_dict(r) for r in data.get("rules", [])]
        return cls(
            version=data.get("version", "1.0"),
            name=data.get("name", "default"),
            name_ar=data.get("name_ar", ""),
            description=data.get("description", ""),
            description_ar=data.get("description_ar", ""),
            enabled=data.get("enabled", True),
            rules=rules,
            tool_allowlist=data.get("tool_allowlist", []),
            domain_allowlist=data.get("domain_allowlist", []),
            blocked_patterns=data.get("blocked_patterns", []),
            dangerous_commands=data.get("dangerous_commands", []),
            limits=data.get("limits", {}),
            metadata=data.get("metadata", {}),
        )

    def add_rule(self, rule: PolicyRule) -> None:
        """Add a rule to the policy"""
        self.rules.append(rule)
        self.updated_at = datetime.now(UTC)

    def remove_rule(self, rule_id: str) -> bool:
        """Remove a rule by ID"""
        for i, rule in enumerate(self.rules):
            if rule.id == rule_id:
                del self.rules[i]
                self.updated_at = datetime.now(UTC)
                return True
        return False

    def get_rule(self, rule_id: str) -> PolicyRule | None:
        """Get a rule by ID"""
        for rule in self.rules:
            if rule.id == rule_id:
                return rule
        return None


def load_policy(path: str | Path) -> GuardPolicy:
    """
    Load policy from JSON file.
    تحميل السياسة من ملف JSON
    """
    path = Path(path)
    if not path.exists():
        return GuardPolicy()

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    return GuardPolicy.from_dict(data)


def save_policy(policy: GuardPolicy, path: str | Path) -> None:
    """
    Save policy to JSON file.
    حفظ السياسة في ملف JSON
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(policy.to_dict(), f, indent=2, ensure_ascii=False)


def create_default_policy() -> GuardPolicy:
    """
    Create default SAHOOL guard policy.
    إنشاء سياسة الحماية الافتراضية لسهول
    """
    return GuardPolicy(
        version="1.0",
        name="sahool-default",
        name_ar="سياسة سهول الافتراضية",
        description="Default security policy for SAHOOL Copilot",
        description_ar="سياسة الأمان الافتراضية لـ Copilot سهول",
        enabled=True,
        rules=[
            PolicyRule(
                id="rule-001",
                name="Allow RAG operations",
                name_ar="السماح بعمليات RAG",
                type="allow",
                target="rag.*",
                priority=100,
            ),
            PolicyRule(
                id="rule-002",
                name="Allow code analysis",
                name_ar="السماح بتحليل الكود",
                type="allow",
                target="code.analyze",
                priority=90,
            ),
            PolicyRule(
                id="rule-003",
                name="Limit code fixes",
                name_ar="تحديد إصلاحات الكود",
                type="limit",
                target="code.fix",
                conditions={"max_files": 20, "require_backup": True},
                priority=80,
            ),
            PolicyRule(
                id="rule-004",
                name="Block destructive commands",
                name_ar="حظر الأوامر المدمرة",
                type="deny",
                target="*",
                conditions={"pattern": "rm -rf"},
                priority=1000,
            ),
        ],
        limits={
            "max_args_size": 20000,
            "max_prompt_chars": 12000,
            "max_files_changed": 20,
            "request_timeout_s": 30,
        },
        metadata={
            "author": "SAHOOL Platform Team",
            "environment": "production",
        },
    )
