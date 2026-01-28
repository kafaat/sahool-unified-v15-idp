# Automated Code Fixing with Ollama DeepSeek-Coder

## 🚀 Quick Start

This tool scans all Python and Dart files in your project and automatically fixes errors using **Ollama with DeepSeek-Coder**.

### Prerequisites

1. **Install Ollama** (if not already installed):
   ```bash
   # Download from https://ollama.ai
   # Or use winget on Windows:
   winget install Ollama.Ollama
   ```

2. **Pull DeepSeek-Coder model**:
   ```bash
   ollama pull deepseek-coder:latest
   ```

3. **Install Python dependencies**:
   ```bash
   cd apps/services/code-fix-agent
   pip install httpx structlog
   ```

## 📋 Commands

### Fix All Errors (Recommended)

```bash
# Dry run first to see what will be fixed
python fix_all_errors.py --dry-run

# Actually fix all Python and Dart errors
python fix_all_errors.py

# Fix with comprehensive strategy (more thorough fixes)
python fix_all_errors.py --strategy comprehensive
```

### Fix Specific Language

```bash
# Fix only Python files
python fix_all_errors.py --language python

# Fix only Dart files
python fix_all_errors.py --language dart
```

### Fix Specific Directory

```bash
# Fix only a specific path
python fix_all_errors.py --path apps/services/ai-agents-service

# Fix mobile app only
python fix_all_errors.py --path apps/mobile --language dart
```

### Advanced Options

```bash
# Use different Ollama model
python fix_all_errors.py --ollama-model deepseek-coder:6.7b

# Use custom Ollama URL
python fix_all_errors.py --ollama-url http://192.168.1.100:11434

# Use refactor strategy (most aggressive)
python fix_all_errors.py --strategy refactor

# Exclude additional directories
python fix_all_errors.py --exclude node_modules .git venv build tests __pycache__
```

### Use API Instead of Ollama

```bash
# Use the code-fix-agent API service instead
python fix_all_errors.py --use-api
```

## 🎯 Fix Strategies

- **minimal** (default): Minimum changes to fix errors
- **comprehensive**: Fix errors + improve code quality
- **refactor**: Fix errors + refactor for better design

## 🔧 Configuration

Set environment variables to customize defaults:

```bash
# Windows PowerShell
$env:OLLAMA_URL="http://localhost:11434"
$env:OLLAMA_MODEL="deepseek-coder:latest"

# Linux/Mac
export OLLAMA_URL="http://localhost:11434"
export OLLAMA_MODEL="deepseek-coder:latest"
```

## 📊 What It Does

1. **Scans** all `.py` and `.dart` files in your project
2. **Detects** syntax errors, type errors, import errors, etc.
3. **Uses DeepSeek-Coder** (via Ollama) to generate intelligent fixes
4. **Applies** fixes automatically to your files
5. **Reports** summary of what was fixed

## ⚠️ Safety

- Always use `--dry-run` first to preview changes
- The tool backs up nothing - commit your changes to git first!
- Review the fixes before committing

## 🤖 How It Works

The tool uses **Ollama** with **DeepSeek-Coder**, a specialized code LLM that:
- Understands code context and semantics
- Generates accurate, minimal fixes
- Preserves code style and structure
- Provides explanations for changes

## 📝 Example Output

```
==========================================
BATCH FIX SUMMARY - Powered by Ollama DeepSeek-Coder
==========================================
Total files scanned: 150
Files fixed: 12
Files skipped (no errors): 135
Files failed: 3

🤖 Using Ollama with deepseek-coder:latest
==========================================
```

## 🐛 Troubleshooting

**Ollama not running:**
```bash
# Start Ollama service
ollama serve
```

**Model not found:**
```bash
# Pull the model
ollama pull deepseek-coder:latest
```

**Timeout errors:**
- Increase timeout in `ollama_client.py` (default: 120s)
- Use a smaller model: `deepseek-coder:6.7b`

## 📚 More Info

- [Ollama Documentation](https://github.com/ollama/ollama)
- [DeepSeek-Coder](https://github.com/deepseek-ai/DeepSeek-Coder)
