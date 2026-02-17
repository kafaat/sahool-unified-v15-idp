<<<<<<< HEAD
# Code Review Agent

AI-powered code review agent using the Claude Agent SDK. Analyzes codebases for bugs, security vulnerabilities, performance issues, and code quality problems.

## Features

- **Comprehensive Analysis**: Bugs, security, performance, and code quality
- **Specialized Subagents**: Security scanner, test analyzer, performance analyzer
- **Structured Output**: JSON Schema-validated results
- **Multiple Formats**: JSON, Markdown, SARIF (GitHub Code Scanning)
- **Audit Logging**: Track all tool usage for compliance
- **Permission Controls**: Block dangerous commands

## Quick Start

```bash
# Install dependencies
npm install

# Run basic review on current directory
npm run review

# Run with structured output
npm run review:structured

# Run production agent
npm run review:production ./src
```

## Usage
=======
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

## Quick Start | البدء السريع

```bash
# Install dependencies | تثبيت المتطلبات
npm install

# Run basic review on current directory | تشغيل المراجعة الأساسية على المجلد الحالي
npm run review

# Run with structured output | التشغيل مع مخرجات منظمة
npm run review:structured

# Run production agent | تشغيل وكيل الإنتاج
npm run review:production ./src
```

## Usage | الاستخدام
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473

### CLI

```bash
<<<<<<< HEAD
# Review current directory
npx tsx src/review-agent.ts

# Review specific directory
npx tsx src/review-agent.ts ./src

# Production agent with all features
npx tsx src/production-agent.ts ./src

# Disable subagents
npx tsx src/production-agent.ts ./src --no-subagents

# Export as Markdown
npx tsx src/production-agent.ts ./src --export --markdown

# Export as SARIF
npx tsx src/production-agent.ts ./src --export --sarif
```

### Programmatic
=======
# Review current directory | مراجعة المجلد الحالي
npx tsx src/review-agent.ts

# Review specific directory | مراجعة مجلد معين
npx tsx src/review-agent.ts ./src

# Production agent with all features | وكيل الإنتاج مع جميع الميزات
npx tsx src/production-agent.ts ./src

# Disable subagents | تعطيل الوكلاء الفرعيين
npx tsx src/production-agent.ts ./src --no-subagents

# Export as Markdown | التصدير كـ Markdown
npx tsx src/production-agent.ts ./src --export --markdown

# Export as SARIF | التصدير كـ SARIF
npx tsx src/production-agent.ts ./src --export --sarif
```

### Programmatic | برمجياً
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473

```typescript
import {
  runCodeReview,
  printResults,
  exportResults,
} from "@sahool/code-review-agent";

<<<<<<< HEAD
// Run review
=======
// Run review | تشغيل المراجعة
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473
const result = await runCodeReview({
  directory: "./src",
  model: "opus",
  useSubagents: true,
});

if (result) {
<<<<<<< HEAD
  // Print formatted results
  printResults(result);

  // Export as SARIF for GitHub
=======
  // Print formatted results | طباعة النتائج المنسقة
  printResults(result);

  // Export as SARIF for GitHub | التصدير كـ SARIF لـ GitHub
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473
  const sarif = exportResults(result, "sarif");
  fs.writeFileSync("results.sarif", sarif);
}
```

<<<<<<< HEAD
## Configuration

### ReviewAgentConfig

| Option             | Type                            | Default  | Description               |
| ------------------ | ------------------------------- | -------- | ------------------------- |
| `directory`        | `string`                        | Required | Directory to review       |
| `model`            | `'opus' \| 'sonnet' \| 'haiku'` | `'opus'` | Claude model to use       |
| `maxTurns`         | `number`                        | `250`    | Maximum agent turns       |
| `useSubagents`     | `boolean`                       | `true`   | Use specialized subagents |
| `structuredOutput` | `boolean`                       | `true`   | Return structured JSON    |

## Output Formats

### JSON (default)
=======
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
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473

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

<<<<<<< HEAD
GitHub Code Scanning compatible format for CI/CD integration.

### Markdown

Human-readable report format.

## Subagents

The production agent uses specialized subagents:

| Subagent               | Model  | Purpose                                |
| ---------------------- | ------ | -------------------------------------- |
| `security-scanner`     | Sonnet | Deep security vulnerability analysis   |
| `test-analyzer`        | Haiku  | Test coverage evaluation               |
| `performance-analyzer` | Sonnet | Performance optimization opportunities |

## Hooks

### Audit Logger

Logs all tool usage with timestamps:
=======
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
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473

```
[AUDIT] 2025-01-10T12:00:00.000Z - Tool: Read
[AUDIT] 2025-01-10T12:00:01.000Z - Tool: Grep
```

<<<<<<< HEAD
### Dangerous Command Blocker

Blocks commands containing:
=======
### Dangerous Command Blocker | محجوب الأوامر الخطيرة

Blocks commands containing: | حجب الأوامر التي تحتوي على:
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473

- `rm -rf`
- `sudo`
- `chmod 777`
- `curl | sh`
- `wget | sh`

<<<<<<< HEAD
## Environment Variables

| Variable            | Description                     |
| ------------------- | ------------------------------- |
| `ANTHROPIC_API_KEY` | API key for Claude              |
| `LOG_LEVEL`         | Logging level (default: `info`) |

## Development

```bash
# Install dependencies
npm install

# Run in development mode
npm run dev

# Run tests
npm test

# Type check
npm run typecheck

# Lint
=======
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
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473
npm run lint
```

## Docker

```bash
<<<<<<< HEAD
# Build image
docker build -t code-review-agent .

# Run container
=======
# Build image | بناء الصورة
docker build -t code-review-agent .

# Run container | تشغيل الحاوية
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473
docker run -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  -v $(pwd):/code:ro \
  code-review-agent /code
```

<<<<<<< HEAD
## Architecture

```
src/
├── index.ts              # Main exports
├── types.ts              # TypeScript types and JSON Schema
├── agent.ts              # Basic agent example
├── review-agent.ts       # Simple review agent
├── review-structured.ts  # Structured output agent
└── production-agent.ts   # Full production agent
```

## License

Proprietary - KAFAAT
=======
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
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473
