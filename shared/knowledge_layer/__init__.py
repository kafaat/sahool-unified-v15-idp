# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Knowledge Layer - طبقة المعرفة
=================================
A first-class introspection layer over the Decision Kernel. Answers:

    Why this recommendation?     describe_recommendation(rec)
    What depends on X?           who_depends_on("shared.digital_twin.X")
    What's the business meaning? business_meaning(path, lang="ar"|"en")
    How does observable O flow?  flow_of(observable_name)
    Which engine owns module M?  EngineRegistry.role_of(module_path)
    Who owns truth about O?      SourceOfTruthRegistry.authority_for(observable)

Pure Python + YAML. No DB. No service. Composable with governance/services.yaml
(which captures service-level dependencies) — this layer is module + decision
chain + business meaning, one level finer.
"""

from shared.knowledge_layer.introspect import (
    describe_feedback_loop,
    describe_recommendation,
    flow_of,
    who_depends_on,
)
from shared.knowledge_layer.loader import (
    all_manifests,
    business_meaning,
    load_manifest,
)
from shared.knowledge_layer.manifest import (
    DecisionRole,
    EngineRegistry,
    InputSpec,
    ModuleManifest,
    OutputSpec,
    SourceOfTruthRegistry,
)
from shared.knowledge_layer.validators import validate_manifest_against_module

__all__ = [
    "ModuleManifest",
    "DecisionRole",
    "InputSpec",
    "OutputSpec",
    "EngineRegistry",
    "SourceOfTruthRegistry",
    "load_manifest",
    "all_manifests",
    "business_meaning",
    "who_depends_on",
    "describe_recommendation",
    "describe_feedback_loop",
    "flow_of",
    "validate_manifest_against_module",
]
