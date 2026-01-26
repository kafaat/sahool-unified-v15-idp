# Open Source Projects Deep Exploration

**Date**: January 2026
**Author**: AI Research Team
**Status**: Complete

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Eigent - Multi-Agent Platform](#eigent---multi-agent-platform)
3. [Remotion - Programmatic Video](#remotion---programmatic-video)
4. [Tambo - Generative UI SDK](#tambo---generative-ui-sdk)
5. [AionUi - AI Desktop GUI](#aionui---ai-desktop-gui)
6. [SAHOOL Integration Recommendations](#sahool-integration-recommendations)
7. [Implementation Roadmap](#implementation-roadmap)

---

## Executive Summary

| Project | Type | Stars | License | SAHOOL Relevance |
|---------|------|-------|---------|------------------|
| **Eigent** | Multi-Agent Platform | - | Apache 2.0 | ⭐⭐⭐⭐⭐ High |
| **Remotion** | Video as Code | 31.4k | Special | ⭐⭐⭐ Medium |
| **Tambo** | Generative UI SDK | - | MIT | ⭐⭐⭐⭐⭐ High |
| **AionUi** | AI Desktop GUI | 10.9k | Apache 2.0 | ⭐⭐⭐ Medium |

### Key Insights

1. **Eigent** could replace/enhance SAHOOL's multi-agent orchestration system
2. **Tambo** enables dynamic advisory UI based on farmer conversations
3. **Remotion** can generate educational agricultural videos programmatically
4. **AionUi** provides a unified GUI for all SAHOOL AI agents

---

## Eigent - Multi-Agent Platform

### Overview

| Attribute | Value |
|-----------|-------|
| **GitHub** | [eigent-ai/eigent](https://github.com/eigent-ai/eigent) |
| **License** | Apache 2.0 |
| **Framework** | CAMEL (Multi-Agent) |
| **Stack** | FastAPI + React + Electron |

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Eigent Desktop                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  React UI   │  │  Electron   │  │    React Flow       │ │
│  │  (Tailwind) │  │  (Desktop)  │  │  (Visualization)    │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                      FastAPI Backend                         │
├──────────┬──────────┬──────────┬──────────┬────────────────┤
│Developer │ Browser  │ Document │MultiModal│   Custom       │
│  Agent   │  Agent   │  Agent   │  Agent   │   Agents       │
├──────────┴──────────┴──────────┴──────────┴────────────────┤
│                     CAMEL Framework                          │
├─────────────────────────────────────────────────────────────┤
│  vLLM  │  Ollama  │  LM Studio  │  OpenAI  │  Anthropic    │
└─────────────────────────────────────────────────────────────┘
```

### Pre-built Agents

| Agent | Description | Capabilities |
|-------|-------------|--------------|
| **Developer** | Code execution | Terminal commands, file operations |
| **Browser** | Web research | Search, content extraction |
| **Document** | File management | Create, edit, organize |
| **MultiModal** | Media processing | Image, audio analysis |

### MCP Integration

```python
# Built-in MCP tools
- Web browsing
- Code execution
- Notion integration
- Google Suite
- Slack integration

# Custom tools
from eigent import register_mcp_tool

@register_mcp_tool
def sahool_field_data(field_id: str):
    """Fetch SAHOOL field data"""
    return get_field_by_id(field_id)
```

### Human-in-the-Loop

Automatic human intervention requests when:
- Task encounters uncertainty
- Critical decisions required
- Error recovery needed

### Installation

```bash
# Quick start
git clone https://github.com/eigent-ai/eigent.git
cd eigent
npm install
npm run dev

# Backend
cd backend && uv sync
```

### Use Cases Demonstrated

1. Travel itinerary planning with Slack integration
2. Financial reporting from CSV with HTML visualization
3. Market research report generation
4. SEO audits and competitive analysis
5. Duplicate file detection
6. PDF processing with signatures

---

## Remotion - Programmatic Video

### Overview

| Attribute | Value |
|-----------|-------|
| **GitHub** | [remotion-dev/remotion](https://github.com/remotion-dev/remotion) |
| **Stars** | 31.4k ⭐ |
| **License** | Special (may require commercial license) |
| **Stack** | React + TypeScript |

### Core Concept

```
Traditional Video Editing:    Remotion:
┌──────────────────┐         ┌──────────────────┐
│  Timeline-based  │         │   Code-based     │
│  Point & Click   │    →    │   Programmable   │
│  Manual edits    │         │   Reusable       │
│  Export once     │         │   Infinite scale │
└──────────────────┘         └──────────────────┘
```

### Architecture

```tsx
// Video as React Component
import { Composition, useCurrentFrame } from 'remotion';

export const MyVideo: React.FC = () => {
  const frame = useCurrentFrame();

  return (
    <Composition
      id="AgriculturalTip"
      component={AgriculturalTip}
      durationInFrames={150}
      fps={30}
      width={1920}
      height={1080}
    />
  );
};

// Dynamic content from API
const AgriculturalTip: React.FC<{tipId: string}> = ({tipId}) => {
  const tip = useFetch(`/api/tips/${tipId}`);

  return (
    <AbsoluteFill style={{background: '#1a5f2a'}}>
      <Title text={tip.title_ar} />
      <Animation data={tip.animation} />
      <Narration audio={tip.audio_ar} />
    </AbsoluteFill>
  );
};
```

### Key Features

| Feature | Description |
|---------|-------------|
| **Web Technologies** | HTML, CSS, SVG, Canvas, WebGL |
| **Programming** | Variables, functions, APIs, algorithms |
| **React Ecosystem** | Reusable components, Fast Refresh |
| **Real-time Preview** | Instant feedback during development |

### Supported Formats

- MP4, WebM (video)
- GIF (animation)
- PNG sequence (frames)
- Audio integration

### Installation

```bash
# Create new project
npx create-video@latest

# Or add to existing project
npm install remotion @remotion/cli
```

### Statistics

- 31.4k stars
- 1.9k forks
- 29,604 commits
- 301 contributors
- 571 releases

---

## Tambo - Generative UI SDK

### Overview

| Attribute | Value |
|-----------|-------|
| **GitHub** | [tambo-ai/tambo](https://github.com/tambo-ai/tambo) |
| **License** | MIT |
| **Stack** | React + TypeScript + NestJS |
| **Type** | Generative UI SDK |

### Core Concept

```
Traditional Chat:              Tambo Generative UI:
┌──────────────────┐          ┌──────────────────┐
│ User: Show sales │          │ User: Show sales │
│ Bot: Here's data │    →     │ ┌──────────────┐ │
│      in text...  │          │ │ 📊 LineChart │ │
│                  │          │ │ Interactive  │ │
└──────────────────┘          │ └──────────────┘ │
                              └──────────────────┘
```

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     TamboProvider                            │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ useTamboThread  │  │ useTamboInput   │  │ Suggestions │ │
│  │ Messages/Stream │  │ User Input      │  │ AI-powered  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    Component Registry                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │
│  │  Graph   │ │   Form   │ │   Card   │ │  DataTable   │   │
│  │ (Chart)  │ │ (Input)  │ │ (Display)│ │ (Grid)       │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                       LLM Router                             │
│  OpenAI │ Anthropic │ Gemini │ Mistral │ Local (Ollama)    │
└─────────────────────────────────────────────────────────────┘
```

### Component Types

#### 1. Generative Components
Created on-demand, render once:

```typescript
// Register chart component
const components: TamboComponent[] = [{
  name: "IrrigationChart",
  description: "Displays irrigation schedule as a chart",
  component: IrrigationChart,
  propsSchema: z.object({
    fieldId: z.string(),
    data: z.array(z.object({
      date: z.string(),
      amount_mm: z.number(),
    })),
    type: z.enum(["line", "bar"]),
  }),
}];
```

#### 2. Interactable Components
Persistent state, user can refine:

```typescript
// Persistent task board
const TaskBoard = withInteractable(
  TaskBoardBase,
  z.object({
    tasks: z.array(taskSchema),
    filter: z.string().optional(),
  })
);
```

### Integration Example

```tsx
// Setup
import { TamboProvider, useTamboThread } from '@tambo-ai/react';

function App() {
  return (
    <TamboProvider
      apiKey={process.env.TAMBO_API_KEY}
      components={agriculturalComponents}
    >
      <FarmerChat />
    </TamboProvider>
  );
}

// Chat component
function FarmerChat() {
  const { messages, sendMessage } = useTamboThread();

  return (
    <div>
      {messages.map(msg => (
        msg.renderedComponent
          ? <msg.renderedComponent {...msg.props} />
          : <TextMessage text={msg.content} />
      ))}
    </div>
  );
}
```

### MCP Integration

```typescript
// External tool integration
const tools: TamboTool[] = [{
  name: "getFieldNDVI",
  tool: async ({ fieldId }) =>
    fetch(`/api/fields/${fieldId}/ndvi`).then(r => r.json()),
  inputSchema: z.object({ fieldId: z.string() }),
  outputSchema: z.object({
    ndvi: z.number(),
    health: z.enum(["good", "moderate", "poor"])
  }),
}];
```

### Comparison

| Feature | Tambo | Vercel AI SDK | CopilotKit |
|---------|-------|---------------|-----------|
| **AI Component Selection** | ✅ Built-in | ❌ Manual | ⚠️ Via agents |
| **MCP Integration** | ✅ Native | ⚠️ Experimental | ⚠️ Recent |
| **Stateful Components** | ✅ Yes | ❌ No | ⚠️ Patterns |
| **Client-side Tools** | ✅ Declarative | ❌ Manual | ❌ Agent-side |

### Pricing

| Tier | Price | Messages/month |
|------|-------|----------------|
| Free | $0 | 10,000 |
| Growth | $25 | 200,000 |
| Enterprise | Custom | Unlimited |

---

## AionUi - AI Desktop GUI

### Overview

| Attribute | Value |
|-----------|-------|
| **GitHub** | [iOfficeAI/AionUi](https://github.com/iOfficeAI/AionUi) |
| **Stars** | 10.9k ⭐ |
| **License** | Apache 2.0 |
| **Stack** | TypeScript + Electron + Python |

### Supported AI Tools

```
┌─────────────────────────────────────────────────────────────┐
│                        AionUi                                │
├─────────────────────────────────────────────────────────────┤
│  Command-Line Tools (Auto-detected):                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ Gemini   │ │ Claude   │ │ Qwen     │ │ Goose    │       │
│  │ CLI      │ │ Code     │ │ Code     │ │ CLI      │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
├─────────────────────────────────────────────────────────────┤
│  Cloud Models:                                               │
│  Google Gemini │ OpenAI │ Anthropic │ Qwen │ DeepSeek      │
├─────────────────────────────────────────────────────────────┤
│  Local Models:                                               │
│  Ollama │ LM Studio │ Custom API                            │
└─────────────────────────────────────────────────────────────┘
```

### Key Features

#### Multi-Agent Mode
```
┌─────────────────────────────────────────┐
│  Session 1: Gemini (Research)           │
│  Session 2: Claude Code (Development)   │
│  Session 3: Qwen (Documentation)        │
│  Each with independent context memory   │
└─────────────────────────────────────────┘
```

#### File Management
- Tree-based file browsing
- Drag-and-drop upload
- AI-powered folder organization
- Batch renaming

#### Preview Panel (9+ formats)
| Format | Support |
|--------|---------|
| PDF | ✅ Full |
| Word | ✅ Full |
| Excel | ✅ Full |
| PowerPoint | ✅ Full |
| Code | ✅ Syntax highlighting |
| Markdown | ✅ Rendered + Edit |
| Images | ✅ View + AI analysis |
| HTML | ✅ Rendered |
| Diff | ✅ Side-by-side |

#### WebUI Remote Access
```bash
# Local access
AionUi --webui

# Remote access (LAN)
AionUi --webui --remote
```

### Comparison with Claude Cowork

| Feature | Claude Cowork | AionUi |
|---------|---------------|--------|
| **OS** | macOS only | Windows, macOS, Linux |
| **Models** | Claude only | 5+ providers + local |
| **Interface** | GUI | GUI + WebUI |
| **Cost** | $100/month | Free |
| **Preview** | Limited | 9+ formats |

### System Requirements

| OS | Requirement |
|----|-------------|
| macOS | 10.15+ |
| Windows | 10+ |
| Linux | Ubuntu 18.04+, Debian 10+, Fedora 32+ |
| RAM | 4GB minimum |
| Storage | 500MB |

### Privacy

- All data stored in local SQLite
- No cloud upload (unless configured)
- WebUI still uses local storage

---

## SAHOOL Integration Recommendations

### 1. Eigent → SAHOOL Multi-Agent System

**Current SAHOOL Architecture**:
```
shared/ai/
├── agents/
│   ├── farm_advisor.py
│   ├── planner.py
│   └── react_agent.py
└── orchestration/
    ├── swarm.py
    └── consensus.py
```

**Recommended Enhancement**:

```python
# shared/ai/eigent_integration.py

from eigent import EigentOrchestrator, Agent

class SAHOOLEigentOrchestrator:
    """
    Integrate Eigent's CAMEL-based multi-agent system
    with SAHOOL's agricultural domain.
    """

    def __init__(self):
        self.orchestrator = EigentOrchestrator()

        # Register SAHOOL-specific agents
        self.orchestrator.register_agent(
            IrrigationAdvisorAgent(),
            FertilizerExpertAgent(),
            PestControlAgent(),
            CropPlannerAgent(),
            MarketAnalystAgent(),
        )

    async def execute_complex_task(self, task: str):
        """
        Execute complex agricultural task with
        multiple agents working in parallel.
        """
        return await self.orchestrator.run(
            task=task,
            human_in_the_loop=True,
            max_iterations=10,
        )

# Usage
orchestrator = SAHOOLEigentOrchestrator()
result = await orchestrator.execute_complex_task(
    "تحليل شامل لحقل القمح: الري، التسميد، مكافحة الآفات"
)
```

**Benefits**:
- ✅ Parallel agent execution
- ✅ Human-in-the-loop for critical decisions
- ✅ MCP integration for external tools
- ✅ Visual workflow in React Flow

---

### 2. Tambo → SAHOOL Advisory Chat

**Recommended Implementation**:

```tsx
// apps/web/src/components/FarmerChat.tsx

import { TamboProvider, useTamboThread } from '@tambo-ai/react';
import { z } from 'zod';

// Register agricultural components
const agriculturalComponents = [
  {
    name: "IrrigationSchedule",
    description: "عرض جدول الري للحقل",
    component: IrrigationScheduleChart,
    propsSchema: z.object({
      fieldId: z.string(),
      schedule: z.array(z.object({
        date: z.string(),
        amount_mm: z.number(),
        duration_hours: z.number(),
      })),
    }),
  },
  {
    name: "NDVIMap",
    description: "خريطة صحة المحصول NDVI",
    component: NDVIMapVisualization,
    propsSchema: z.object({
      fieldId: z.string(),
      ndviData: z.array(z.object({
        lat: z.number(),
        lng: z.number(),
        value: z.number(),
      })),
    }),
  },
  {
    name: "CropAdvisoryCard",
    description: "بطاقة استشارة زراعية",
    component: CropAdvisoryCard,
    propsSchema: z.object({
      title: z.string(),
      title_ar: z.string(),
      priority: z.enum(["critical", "warning", "info"]),
      actions: z.array(z.object({
        action: z.string(),
        action_ar: z.string(),
        deadline: z.string().optional(),
      })),
    }),
  },
  {
    name: "WeatherForecast",
    description: "توقعات الطقس للمزرعة",
    component: WeatherForecastWidget,
    propsSchema: z.object({
      farmId: z.string(),
      days: z.number().default(7),
    }),
  },
];

// SAHOOL tools for Tambo
const sahoolTools = [
  {
    name: "getFieldData",
    tool: async ({ fieldId }) =>
      fetch(`/api/fields/${fieldId}`).then(r => r.json()),
    inputSchema: z.object({ fieldId: z.string() }),
  },
  {
    name: "getNDVI",
    tool: async ({ fieldId }) =>
      fetch(`/api/fields/${fieldId}/ndvi`).then(r => r.json()),
    inputSchema: z.object({ fieldId: z.string() }),
  },
  {
    name: "getIrrigationRecommendation",
    tool: async ({ fieldId }) =>
      fetch(`/api/advisory/irrigation/${fieldId}`).then(r => r.json()),
    inputSchema: z.object({ fieldId: z.string() }),
  },
];

export function FarmerAdvisoryChat() {
  return (
    <TamboProvider
      apiKey={process.env.NEXT_PUBLIC_TAMBO_API_KEY}
      components={agriculturalComponents}
      tools={sahoolTools}
    >
      <ChatInterface />
    </TamboProvider>
  );
}
```

**User Experience**:
```
المزارع: "أرني حالة حقل القمح رقم 3"

┌────────────────────────────────────────┐
│  🌾 حقل القمح #3                       │
│  ├─ NDVI: 0.72 (جيد)                   │
│  ├─ رطوبة التربة: 45%                  │
│  └─ المرحلة: التفريع                   │
│                                        │
│  📊 [NDVI Map Interactive]             │
│                                        │
│  ⚠️ توصية: الري خلال 48 ساعة          │
│  └─ [تنفيذ] [تأجيل] [المزيد]          │
└────────────────────────────────────────┘
```

---

### 3. Remotion → Agricultural Education Videos

**Recommended Implementation**:

```tsx
// packages/video-generator/src/compositions/IrrigationTip.tsx

import { Composition, useCurrentFrame, interpolate } from 'remotion';

interface IrrigationTipProps {
  cropType: string;
  cropType_ar: string;
  tipText: string;
  tipText_ar: string;
  schedule: { day: number; amount_mm: number }[];
}

export const IrrigationTipVideo: React.FC<IrrigationTipProps> = ({
  cropType_ar,
  tipText_ar,
  schedule,
}) => {
  const frame = useCurrentFrame();

  const titleOpacity = interpolate(frame, [0, 30], [0, 1]);
  const chartProgress = interpolate(frame, [30, 90], [0, 1]);

  return (
    <AbsoluteFill style={{ background: '#1a5f2a' }}>
      {/* Title */}
      <div style={{ opacity: titleOpacity, textAlign: 'right' }}>
        <h1 style={{ color: 'white', fontSize: 48 }}>
          نصيحة ري {cropType_ar}
        </h1>
      </div>

      {/* Animated Chart */}
      <AnimatedIrrigationChart
        data={schedule}
        progress={chartProgress}
      />

      {/* Tip Text */}
      <div style={{
        position: 'absolute',
        bottom: 100,
        right: 50,
        color: 'white',
        fontSize: 32,
        textAlign: 'right',
      }}>
        {tipText_ar}
      </div>

      {/* SAHOOL Logo */}
      <Logo />
    </AbsoluteFill>
  );
};

// Register composition
export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="IrrigationTip"
        component={IrrigationTipVideo}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          cropType: "wheat",
          cropType_ar: "القمح",
          tipText_ar: "يُنصح بالري كل 10-14 يوم في مرحلة التفريع",
          schedule: [
            { day: 1, amount_mm: 25 },
            { day: 10, amount_mm: 30 },
            { day: 20, amount_mm: 25 },
          ],
        }}
      />
    </>
  );
};
```

**Batch Video Generation**:

```typescript
// scripts/generate-advisory-videos.ts

import { bundle } from '@remotion/bundler';
import { renderMedia } from '@remotion/renderer';

async function generateAdvisoryVideos() {
  const tips = await fetch('/api/advisory/tips').then(r => r.json());

  const bundled = await bundle('./src/index.ts');

  for (const tip of tips) {
    await renderMedia({
      composition: 'IrrigationTip',
      serveUrl: bundled,
      codec: 'h264',
      outputLocation: `./output/${tip.id}.mp4`,
      inputProps: {
        cropType_ar: tip.crop_ar,
        tipText_ar: tip.text_ar,
        schedule: tip.schedule,
      },
    });

    console.log(`Generated video for tip: ${tip.id}`);
  }
}
```

---

### 4. AionUi → SAHOOL Admin Interface

**Recommended Use Cases**:

1. **Unified Agent Management**
   - GUI for all SAHOOL AI agents
   - Switch between Claude, Gemini, local Ollama
   - Independent sessions per task

2. **Document Processing**
   - Farm contracts (PDF)
   - Soil analysis reports (Word/Excel)
   - Compliance documents

3. **Preview Integration**
   - NDVI maps
   - Agricultural reports
   - Generated videos

**Configuration**:
```bash
# AionUi with SAHOOL custom tools
AionUi --config sahool-config.json --webui --remote
```

```json
// sahool-config.json
{
  "agents": [
    {
      "name": "SAHOOL Advisor",
      "command": "python -m sahool.advisor",
      "model": "ollama:llama3"
    },
    {
      "name": "Field Analyst",
      "command": "python -m sahool.analyst",
      "model": "gemini-2.5-flash"
    }
  ],
  "tools": {
    "sahool_api": "http://localhost:8000"
  }
}
```

---

## Implementation Roadmap

### Phase 1: Tambo Integration (2-3 weeks)

| Task | Priority | Effort |
|------|----------|--------|
| Setup TamboProvider | High | 2 days |
| Register agricultural components | High | 1 week |
| Implement SAHOOL tools | High | 3 days |
| Testing & refinement | Medium | 3 days |

### Phase 2: Eigent Multi-Agent (3-4 weeks)

| Task | Priority | Effort |
|------|----------|--------|
| Eigent setup & configuration | High | 3 days |
| Create SAHOOL-specific agents | High | 2 weeks |
| MCP tool integration | Medium | 1 week |
| Human-in-the-loop flows | Medium | 3 days |

### Phase 3: Remotion Video Generator (2 weeks)

| Task | Priority | Effort |
|------|----------|--------|
| Remotion setup | Medium | 2 days |
| Create agricultural compositions | Medium | 1 week |
| Batch generation pipeline | Medium | 3 days |

### Phase 4: AionUi Admin (Optional)

| Task | Priority | Effort |
|------|----------|--------|
| Deploy AionUi | Low | 1 day |
| Configure SAHOOL agents | Low | 2 days |
| Custom tool integration | Low | 3 days |

---

## Summary

### Highest Priority for SAHOOL

1. **Tambo** - Immediate value for farmer-facing advisory chat
2. **Eigent** - Enhance multi-agent orchestration capabilities
3. **Remotion** - Scalable educational content generation
4. **AionUi** - Admin productivity tool

### Technical Alignment

| Project | SAHOOL Stack Compatibility |
|---------|---------------------------|
| Eigent | ✅ FastAPI, React, Python |
| Tambo | ✅ React, TypeScript, NestJS |
| Remotion | ✅ React, TypeScript |
| AionUi | ✅ Electron, TypeScript |

---

## References

- [Eigent GitHub](https://github.com/eigent-ai/eigent)
- [Remotion GitHub](https://github.com/remotion-dev/remotion)
- [Tambo GitHub](https://github.com/tambo-ai/tambo)
- [AionUi GitHub](https://github.com/iOfficeAI/AionUi)
- [CAMEL Framework](https://github.com/camel-ai/camel)
- [Remotion Documentation](https://remotion.dev/docs)
- [Tambo Documentation](https://tambo.ai/docs)

---

*Document generated: January 2026*
*Last updated: 2026-01-26*
