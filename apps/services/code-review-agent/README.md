# Code Review Agent | وكيل مراجعة الكود

**English:** AI-powered code review agent using the Claude Agent SDK. Analyzes codebases for bugs, security vulnerabilities, performance issues, and code quality problems.

**العربية:** وكيل مراجعة الكود الذي يعمل بالذكاء الاصطناعي باستخدام Claude Agent SDK. يحلل قواعد البيانات للبحث عن الأخطاء والثغرات الأمنية ومشاكل الأداء ومشاكل جودة الكود.

## Features | الميزات

- **Comprehensive Analysis**: Bugs, security, performance, and code quality
  - **التحليل الشامل**: الأخطاء والأمان والأداء وجودة الكود
- **Specialized Subagents**: Security scanner, test analyzer, performance analyzer
  - **وكلاء متخصصون**: ماسح الأمان ومحلل الاختبارات ومحلل الأداء
- **Structured Output**: JSON Schema-validated results
  - **المخرجات المنظمة**: نتائج موثقة بـ JSON Schema
- **Multiple Formats**: JSON, Markdown, SARIF (GitHub Code Scanning)
  - **صيغ متعددة**: JSON و Markdown و SARIF (مسح كود GitHub)
- **Audit Logging**: Track all tool usage for compliance
  - **تسجيل التدقيق**: تتبع جميع استخدام الأدوات للامتثال
- **Permission Controls**: Block dangerous commands
  - **التحكم في الأذونات**: حجب الأوامر الخطيرة

## Running as a Docker job | التشغيل كـ Docker job

> **Note:** This agent is a **one-shot CLI job**, not a long-running
> service. Its Dockerfile CMD (`node dist/production-agent.js`) runs
> a review, writes output, and exits. Starting it with
> `docker compose up` would leave a confusing `Exited (0)` container
> in `docker ps -a`, so it is gated behind the `ai-agents` compose
> profile — it will not start by default.
>
> **ملاحظة:** هذا الوكيل مهمّة CLI تُنفَّذ مرّة واحدة، وليس خدمة
> طويلة الأمد. لذا مُغلَق خلف الـ profile `ai-agents` ولن يبدأ
> افتراضيّاً مع بقيّة الخدمات.

```bash
# One-shot invocation (recommended):
ANTHROPIC_API_KEY=sk-... \
  docker compose --profile ai-agents run --rm code-review-agent \
    --repo /app --output /app/review.md --format markdown

# Emit SARIF for GitHub Code Scanning:
ANTHROPIC_API_KEY=sk-... \
  docker compose --profile ai-agents run --rm code-review-agent \
    --repo /app --output /app/review.sarif --format sarif

# Pre-build the image without running it:
docker compose --profile ai-agents build code-review-agent
```

## Quick Start | البدء السريع

```bash
# Install dependencies | تثبيت المتطلبات
npm install

# Review current directory, print JSON to stdout | مراجعة المجلد الحالي
npx tsx src/production-agent.ts --repo .

# Review a specific path and save a Markdown report | مراجعة مسار محدد
npx tsx src/production-agent.ts --repo ./src --output review.md --format markdown

# Emit SARIF for CI integration | إخراج SARIF لـ CI
npx tsx src/production-agent.ts --repo ./src --output review.sarif --format sarif
```

## Usage | الاستخدام

### CLI

```bash
# Show help | عرض المساعدة
npx tsx src/production-agent.ts --help

# Review current directory (JSON to stdout) | مراجعة المجلد الحالي
npx tsx src/production-agent.ts --repo .

# Review a specific directory | مراجعة مجلد معين
npx tsx src/production-agent.ts --repo ./src

# Write Markdown report to a file | كتابة تقرير Markdown إلى ملف
npx tsx src/production-agent.ts --repo ./src --output review.md --format markdown

# Emit SARIF for GitHub Code Scanning | إخراج SARIF لمسح كود GitHub
npx tsx src/production-agent.ts --repo ./src --output review.sarif --format sarif

# Disable specialized subagents (faster, shallower review) | تعطيل الوكلاء الفرعيين
npx tsx src/production-agent.ts --repo ./src --no-subagents

# Pick a cheaper/faster model | اختيار نموذج أسرع/أرخص
npx tsx src/production-agent.ts --repo ./src --model haiku

# Cap the number of agent turns | تحديد عدد دورات الوكيل
npx tsx src/production-agent.ts --repo ./src --max-turns 100
```

#### Flags | الخيارات

| Flag             | Default  | Description                                 | الوصف                             |
| ---------------- | -------- | ------------------------------------------- | --------------------------------- |
| `--repo <path>`  | `.`      | Directory to review                         | المجلد المراد مراجعته             |
| `--output <file>`| stdout   | Write report to file instead of stdout      | كتابة التقرير إلى ملف              |
| `--format <fmt>` | `json`   | Output format: `json`, `markdown`, `sarif`  | صيغة المخرجات                      |
| `--no-subagents` | off      | Skip specialized subagents                  | تخطي الوكلاء المتخصصين             |
| `--model <name>` | `opus`   | Claude model: `opus`, `sonnet`, `haiku`     | نموذج Claude                       |
| `--max-turns <n>`| `250`    | Maximum agent turns                         | الحد الأقصى لدورات الوكيل          |
| `--help`, `-h`   | —        | Show usage and exit                         | عرض الاستخدام                      |

> **Deprecated flags:** `--sarif` and `--markdown` are still accepted as
> aliases for `--format sarif` / `--format markdown` for backward
> compatibility, but will be removed in a future release. Prefer `--format`.
>
> **الخيارات المهجورة:** لا يزال `--sarif` و `--markdown` مقبولين كأسماء
> بديلة، لكنهما سيُزالان لاحقاً. يُفضَّل استخدام `--format`.

### Programmatic | برمجياً

```typescript
import {
  runCodeReview,
  printResults,
  exportResults,
} from "@sahool/code-review-agent";

// Run review | تشغيل المراجعة
const result = await runCodeReview({
  directory: "./src",
  model: "opus",
  useSubagents: true,
});

if (result) {
  // Print formatted results | طباعة النتائج المنسقة
  printResults(result);

  // Export as SARIF for GitHub | التصدير كـ SARIF لـ GitHub
  const sarif = exportResults(result, "sarif");
  fs.writeFileSync("results.sarif", sarif);
}
```

## Configuration | الإعداد

### ReviewAgentConfig

| Option             | Type                            | Default  | Description               | الوصف                              |
| ------------------ | ------------------------------- | -------- | ------------------------- | --------------------------------- |
| `directory`        | `string`                        | Required | Directory to review       | المجلد المراد مراجعته               |
| `model`            | `'opus' \| 'sonnet' \| 'haiku'` | `'opus'` | Claude model to use       | نموذج Claude الذي يجب استخدامه    |
| `maxTurns`         | `number`                        | `250`    | Maximum agent turns       | الحد الأقصى لدورات الوكيل           |
| `useSubagents`     | `boolean`                       | `true`   | Use specialized subagents | استخدام الوكلاء المتخصصين          |
| `structuredOutput` | `boolean`                       | `true`   | Return structured JSON    | إرجاع JSON منظم                     |

## Output Formats | صيغ المخرجات

### JSON (default | الافتراضي)

```json
{
  "issues": [
    {
      "severity": "high",
      "category": "security",
      "file": "src/auth.ts",
      "line": 42,
      "description": "SQL injection vulnerability",
      "suggestion": "Use parameterized queries"
    }
  ],
  "summary": "Found 3 issues...",
  "overallScore": 75
}
```

### SARIF

GitHub Code Scanning compatible format for CI/CD integration. | صيغة متوافقة مع مسح كود GitHub للتكامل مع CI/CD.

### Markdown

Human-readable report format. | صيغة التقرير سهلة القراءة للبشر.

## Subagents | الوكلاء الفرعيون

The production agent uses specialized subagents: | يستخدم وكيل الإنتاج وكلاء فرعيين متخصصين:

| Subagent               | Model  | Purpose                                | الغرض                                    |
| ---------------------- | ------ | -------------------------------------- | ---------------------------------------- |
| `security-scanner`     | Sonnet | Deep security vulnerability analysis   | تحليل عميق للثغرات الأمنية              |
| `test-analyzer`        | Haiku  | Test coverage evaluation               | تقييم تغطية الاختبارات                  |
| `performance-analyzer` | Sonnet | Performance optimization opportunities | فرص تحسين الأداء                         |

## Hooks | الخطاطيف

### Audit Logger | مسجل التدقيق

Logs all tool usage with timestamps: | تسجيل جميع استخدام الأدوات مع الطوابع الزمنية:

```
[AUDIT] 2025-01-10T12:00:00.000Z - Tool: Read
[AUDIT] 2025-01-10T12:00:01.000Z - Tool: Grep
```

### Dangerous Command Blocker | محجوب الأوامر الخطيرة

Blocks commands containing: | حجب الأوامر التي تحتوي على:

- `rm -rf`
- `sudo`
- `chmod 777`
- `curl | sh`
- `wget | sh`

## Environment Variables | متغيرات البيئة

| Variable            | Description                     | الوصف                           |
| ------------------- | ------------------------------- | ------------------------------- |
| `ANTHROPIC_API_KEY` | API key for Claude              | مفتاح API لـ Claude             |
| `LOG_LEVEL`         | Logging level (default: `info`) | مستوى التسجيل (افتراضي: `info`) |

## Development | التطوير

```bash
# Install dependencies | تثبيت المتطلبات
npm install

# Run in development mode | التشغيل في وضع التطوير
npm run dev

# Run tests | تشغيل الاختبارات
npm test

# Type check | فحص النوع
npm run typecheck

# Lint | الفحص اللغوي
npm run lint
```

## Docker

```bash
# Build image | بناء الصورة
docker build -t code-review-agent \
  -f apps/services/code-review-agent/Dockerfile .

# Run container (JSON report to stdout) | تشغيل الحاوية
docker run --rm \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  -v $(pwd):/code:ro \
  code-review-agent --repo /code

# Run container (Markdown report to a host file) | تقرير Markdown إلى ملف
docker run --rm \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  -v $(pwd):/code \
  code-review-agent --repo /code --output /code/review.md --format markdown
```

## Architecture | الهندسة المعمارية

```
src/
├── index.ts              # Main exports | المخرجات الرئيسية
├── types.ts              # TypeScript types and JSON Schema | أنواع TypeScript وـ JSON Schema
├── agent.ts              # Basic agent example | مثال وكيل أساسي
├── review-agent.ts       # Simple review agent | وكيل مراجعة بسيط
├── review-structured.ts  # Structured output agent | وكيل المخرجات المنظمة
└── production-agent.ts   # Full production agent | وكيل الإنتاج الكامل
```

## License | الترخيص

Proprietary - KAFAAT | ملكية خاصة - KAFAAT
