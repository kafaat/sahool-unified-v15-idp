# SAHOOL AI Skills Library | مكتبة مهارات الذكاء الاصطناعي

Unified index of all Claude Code skills in this repository. Each skill is an `.md` file with YAML frontmatter (`name`, `description` with `TRIGGER when ...`) for auto-discovery by Claude Code, and is portable to ChatGPT, Gemini, Cursor, or any agent orchestrator.

**Totals**: 29 local skills across 9 categories, plus 6 bundled plugin skills (next.js, docker, postgres).

---

## Quick Discovery

| I want to... | Use skill | Category |
|---|---|---|
| Write an article/thread with logical flow | `scqa-writing-framework` | writing-content |
| Turn a blog into threads + video scripts | `content-repurposing-engine` | writing-content |
| Match a brand voice across outputs | `tone-style-enforcer` | writing-content |
| TL;DR a long document | `long-form-summary-compressor` | writing-content |
| Write marketing/landing copy with CTA | `structured-copywriting` | writing-content |
| Draw a system diagram | `excalidraw-diagram-generator` | visual-infographic |
| Build a visual summary/infographic | `infographic-builder` | visual-infographic |
| Map a decision tree | `flowchart-decision-builder` | visual-infographic |
| Review a UI layout | `ui-ux-layout-advisor` | visual-infographic |
| Synthesize insights from many sources | `deep-research-synthesizer` | research-analysis |
| Decode a blockchain transaction | `onchain-transaction-analyzer` | research-analysis |
| Validate credibility of citations | `source-validation` | research-analysis |
| Compare tools/protocols (SWOT) | `competitive-intelligence` | research-analysis |
| Structure messy notes into a framework | `knowledge-structuring` | research-analysis |
| Write a video script with hook + CTA | `video-script-generator` | content-creation |
| Plan scene cuts & transitions | `video-editing-planner` | content-creation |
| Generate 10 hook options | `hook-generator` | content-creation |
| Format SRT/VTT captions | `caption-subtitle-formatter` | content-creation |
| Review code outside SAHOOL monorepo | `code-review-generic` | coding-automation |
| Decompose a goal into agent workflow | `workflow-automation-agent` | coding-automation |
| Generate a new skill `.md` file | `skill-creator` | coding-automation |
| Plan a deployment / rollback | `devops-assistant` | coding-automation |
| Compress SAHOOL farm data for LLM context | `context-compression` | context-engineering |
| Store/query farm memory (fields, events) | `memory` | context-engineering |
| Evaluate agricultural advisory quality | `evaluation` (LLM-as-Judge) | context-engineering |
| Generate bilingual crop advisory | `crop-advisor` | sahool |
| Write Obsidian-compatible farm docs | `farm-documentation` | sahool |
| Scaffold a SAHOOL microservice | `service-scaffolding` (sahool) / `service-scaffold` (development) | sahool / development |
| Review SAHOOL code for platform standards | `code-review` | development |
| Write SAHOOL tests | `testing` | development |
| Format Obsidian markdown | `markdown` | obsidian |
| Build Obsidian canvas knowledge graph | `canvas` | obsidian |

---

## General-Purpose Library (22 skills)

Portable skills usable in any project or AI tool. Sourced from the exploraX "20 Powerful Agentic Skills" article ([x.com/explorax_/status/2039269234253934811](https://x.com/explorax_/status/2039269234253934811)) and adapted to SAHOOL's auto-discovery frontmatter format.

### writing-content/ (5)

| Skill | Purpose |
|---|---|
| [scqa-writing-framework](writing-content/scqa-writing-framework.md) | Situation-Complication-Question-Answer narrative structure |
| [content-repurposing-engine](writing-content/content-repurposing-engine.md) | Long-form → threads, scripts, summaries |
| [tone-style-enforcer](writing-content/tone-style-enforcer.md) | Enforce brand voice across outputs |
| [long-form-summary-compressor](writing-content/long-form-summary-compressor.md) | Digest long articles into TL;DRs |
| [structured-copywriting](writing-content/structured-copywriting.md) | Persuasive copy with hooks + CTA |

### visual-infographic/ (4)

| Skill | Purpose |
|---|---|
| [excalidraw-diagram-generator](visual-infographic/excalidraw-diagram-generator.md) | Text → Excalidraw-style nodes |
| [infographic-builder](visual-infographic/infographic-builder.md) | Structured visual summaries |
| [flowchart-decision-builder](visual-infographic/flowchart-decision-builder.md) | Decision trees & process flows |
| [ui-ux-layout-advisor](visual-infographic/ui-ux-layout-advisor.md) | Interface layout & hierarchy review |

### research-analysis/ (5)

| Skill | Purpose |
|---|---|
| [deep-research-synthesizer](research-analysis/deep-research-synthesizer.md) | Extract insights from large datasets |
| [onchain-transaction-analyzer](research-analysis/onchain-transaction-analyzer.md) | Trace wallets, contracts, token flows |
| [source-validation](research-analysis/source-validation.md) | Credibility & bias assessment |
| [competitive-intelligence](research-analysis/competitive-intelligence.md) | Compare products/protocols (SWOT) |
| [knowledge-structuring](research-analysis/knowledge-structuring.md) | Organize unstructured notes |

### content-creation/ (4)

| Skill | Purpose |
|---|---|
| [video-script-generator](content-creation/video-script-generator.md) | Hooks + sections + CTA for video |
| [video-editing-planner](content-creation/video-editing-planner.md) | Scene cuts, transitions, pacing |
| [hook-generator](content-creation/hook-generator.md) | Attention-grabbing openers |
| [caption-subtitle-formatter](content-creation/caption-subtitle-formatter.md) | SRT/VTT formatting & timing |

### coding-automation/ (4)

| Skill | Purpose |
|---|---|
| [code-review-generic](coding-automation/code-review-generic.md) | Language-agnostic code review (non-SAHOOL) |
| [workflow-automation-agent](coding-automation/workflow-automation-agent.md) | Decompose goals into agent steps |
| [skill-creator](coding-automation/skill-creator.md) | Meta-skill: scaffold new `.md` skills |
| [devops-assistant](coding-automation/devops-assistant.md) | Generic git/deploy/CI guidance |

---

## SAHOOL-Specific Skills (7)

Platform-aware skills that know about SAHOOL contracts, NATS events, Arabic/RTL, PostGIS, and tenant scoping. **Prefer these over the generic library when working inside this monorepo.**

### context-engineering/ (3)

| Skill | Purpose |
|---|---|
| [context-compression](context-engineering/compression.md) | 3-level agricultural context compression (preserves PHI, dosages, RPW alerts) |
| [memory](context-engineering/memory.md) | Farm memory: fields, events, decisions, outcomes |
| [evaluation](context-engineering/evaluation.md) | LLM-as-Judge for advisory quality (accuracy/safety/timeliness) |

### sahool/ (3)

| Skill | Purpose |
|---|---|
| [crop-advisor](sahool/crop-advisor.md) | Bilingual crop advisory (wheat, barley, date palm, vegetables) |
| [farm-documentation](sahool/farm-documentation.md) | Obsidian-compatible farm docs with bilingual frontmatter |
| [service-scaffolding](sahool/service-scaffolding.md) | Scaffold SAHOOL microservice from IDP templates |

### development/ (3)

| Skill | Purpose |
|---|---|
| [code-review](development/code-review.md) | SAHOOL platform code review (contracts, ports, NATS subjects) |
| [service-scaffold](development/service-scaffold.md) | Generate FastAPI/NestJS scaffolds matching SAHOOL conventions |
| [testing](development/testing.md) | Pytest markers, coverage, SAHOOL test folder layout |

### obsidian/ (2)

| Skill | Purpose |
|---|---|
| [markdown](obsidian/markdown.md) | Obsidian wikilinks, callouts, dataview queries |
| [canvas](obsidian/canvas.md) | Obsidian canvas knowledge graphs |

---

## Bundled Plugin Skills

These come from installed Claude Code plugins. Not part of this repository but available in sessions:

- **docker-development** — Dockerfile, multi-stage builds, compose
- **docker-compose-orchestration** — Compose networking, volumes, prod deploy
- **next-best-practices** — Next.js 15 RSC, data patterns, metadata
- **next-upgrade** — Next.js version migration
- **postgres-best-practices** — Schema design, indexes, migrations

Plus skills loaded dynamically via MCP or the Skill tool (e.g., `commit`, `check-contracts`, `fixops-run`, `service-health`, `sync-dart-contracts`).

---

## Usage Patterns

### Auto-discovery (default)

Write a natural request. Claude Code reads each skill's `TRIGGER when ...` clause and activates matching ones automatically:

```
> اكتب thread عن ميزة NDVI
# activates: scqa-writing-framework + hook-generator

> لخّص هذا التقرير الزراعي للحفاظ على token budget
# activates: context-compression (SAHOOL)

> راجع هذا السكربت Python
# activates: code-review-generic
```

### Explicit invocation

Use the Skill tool or slash command:

```
/scqa-writing-framework
/crop-advisor
/context-compression
```

### Chaining for real workflows

| Goal | Skill chain |
|---|---|
| Launch announcement for NDVI feature | `deep-research-synthesizer` → `scqa-writing-framework` → `content-repurposing-engine` → `hook-generator` |
| New microservice end-to-end | `sahool/service-scaffolding` → `development/testing` → `development/code-review` → `/commit` |
| Arabic farmer advisory with audit | `sahool/crop-advisor` → `context-engineering/evaluation` → `sahool/farm-documentation` |
| Competitive analysis deck | `research-analysis/source-validation` → `competitive-intelligence` → `infographic-builder` |

### Porting outside Claude Code

Each `.md` file is self-contained. Copy-paste into:
- **ChatGPT / Gemini** — as a Custom Instruction or Project file
- **Cursor / Windsurf** — as a `.cursorrules` entry
- **OpenCode / Codex** — as system prompt
- **Claude Projects** — upload as knowledge

---

## Disambiguation Rules

Where generic and SAHOOL skills overlap, this is the priority inside the monorepo:

| Task in SAHOOL context | Use | Not |
|---|---|---|
| Compress farm sensor data | `context-engineering/compression` | `writing-content/long-form-summary-compressor` |
| Review SAHOOL microservice code | `development/code-review` | `coding-automation/code-review-generic` |
| Commit SAHOOL changes | `/commit` slash command | `coding-automation/devops-assistant` |
| Validate API contracts | `/check-contracts` | — |
| Scaffold a service | `sahool/service-scaffolding` or `development/service-scaffold` | — |

Outside SAHOOL code (side projects, external reviews, marketing content), the generic library wins.

---

## Adding a New Skill

Use the meta-skill:

```
> استخدم skill-creator لإنشاء مهارة اسمها X تفعل Y
```

Or manually: create `<category>/<slug>.md` with this frontmatter:

```yaml
---
name: your-skill-slug
description: One-sentence purpose. TRIGGER when user asks "...", "...", or provides X. DO NOT TRIGGER when <overlap-case>.
license: Complete terms in LICENSE.txt
---
```

Then re-run auto-discovery (new Claude Code session) and add a row in this README's Quick Discovery table.

---

## Governance

- **License**: Proprietary to KAFAAT / SAHOOL platform
- **Owner**: `group:ai-team` (see `idp/backstage/catalog/`)
- **Source of truth**: This directory (`.claude/skills/`)
- **Related**: `governance/agents.yaml` (11 agent categories), `.claude/skills/sahool/service-scaffolding.md`

---

*Last updated: 2026-04-13 — branch `claude/ai-agent-skills-library-ZHnpK`*
