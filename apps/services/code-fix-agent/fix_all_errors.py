#!/usr/bin/env python3
"""
Batch Code Fix Script
=====================
سكريبت إصلاح الأخطاء الجماعي

Scans all Python and Dart files in the project and fixes errors using the code-fix-agent.

Usage:
    python fix_all_errors.py [--dry-run] [--language python|dart|all]
"""

import argparse
import asyncio
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import httpx
import structlog

# Import Ollama client
sys.path.insert(0, str(Path(__file__).parent / "src"))
from agent.ollama_client import OllamaClient

logger = structlog.get_logger()

# Configuration
CODE_FIX_AGENT_URL = os.getenv("CODE_FIX_AGENT_URL", "http://localhost:8162")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-coder:latest")
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent  # Go up to project root
USE_OLLAMA = os.getenv("USE_OLLAMA", "true").lower() == "true"  # Use Ollama by default


class ErrorScanner:
    """Scans files for errors"""

    def __init__(self, language: str):
        self.language = language

    def scan_python_file(self, file_path: Path) -> list[dict[str, Any]]:
        """Scan Python file for syntax errors"""
        try:
            # Try to compile the file
            with open(file_path, encoding="utf-8") as f:
                code = f.read()

            compile(code, str(file_path), "exec")
            return []  # No errors
        except SyntaxError as e:
            return [
                {
                    "type": "SyntaxError",
                    "line": e.lineno,
                    "column": e.offset,
                    "message": e.msg,
                    "text": e.text,
                }
            ]
        except Exception as e:
            logger.warning("scan_failed", file=str(file_path), error=str(e))
            return []

    def scan_dart_file(self, file_path: Path) -> list[dict[str, Any]]:
        """Scan Dart file for errors using dart analyze"""
        try:
            result = subprocess.run(
                ["dart", "analyze", str(file_path)],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                return []  # No errors

            # Parse dart analyze output
            errors = []
            for line in result.stdout.split("\n"):
                if "error" in line.lower() or "warning" in line.lower():
                    # Simple parsing - can be improved
                    errors.append(
                        {
                            "type": "DartError",
                            "message": line.strip(),
                        }
                    )

            return errors
        except FileNotFoundError:
            logger.error("dart_not_found", message="Dart SDK not found in PATH")
            return []
        except Exception as e:
            logger.warning("dart_scan_failed", file=str(file_path), error=str(e))
            return []


class CodeFixClient:
    """Client for code-fix-agent API with Ollama support"""

    def __init__(
        self,
        base_url: str,
        use_ollama: bool = True,
        ollama_url: str = None,
        ollama_model: str = None,
    ):
        self.base_url = base_url
        self.use_ollama = use_ollama
        self.client = httpx.AsyncClient(timeout=60.0)

        # Initialize Ollama client if enabled
        if use_ollama:
            self.ollama = OllamaClient(
                base_url=ollama_url or OLLAMA_URL,
                model=ollama_model or OLLAMA_MODEL,
            )
            logger.info("ollama_enabled", url=ollama_url or OLLAMA_URL, model=ollama_model or OLLAMA_MODEL)
        else:
            self.ollama = None

    async def analyze_code(self, code: str, language: str, file_path: str) -> dict[str, Any]:
        """Analyze code for issues"""
        if self.use_ollama and self.ollama:
            # Use Ollama for analysis
            try:
                result = await self.ollama.analyze_code(code, language)
                return {
                    "success": True,
                    "data": {
                        "issues": result.get("issues", []),
                        "summary": result.get("summary", ""),
                    },
                }
            except Exception as e:
                logger.error("ollama_analyze_failed", error=str(e))
                return {"success": False, "error": str(e)}
        else:
            # Use API
            try:
                response = await self.client.post(
                    f"{self.base_url}/api/v1/analyze",
                    json={
                        "code": code,
                        "language": language,
                        "file_path": file_path,
                    },
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error("analyze_failed", error=str(e))
                return {"success": False, "error": str(e)}

    async def fix_code(self, code: str, errors: list[dict], language: str, strategy: str = "minimal") -> dict[str, Any]:
        """Fix code errors"""
        if self.use_ollama and self.ollama:
            # Use Ollama for fixing
            try:
                result = await self.ollama.fix_code(code, errors, language, strategy)
                return {
                    "success": True,
                    "data": {
                        "fixed_code": result.get("fixed_code", code),
                        "changes": result.get("changes", []),
                        "explanation": result.get("explanation", ""),
                    },
                    "confidence": result.get("confidence", 0.7),
                }
            except Exception as e:
                logger.error("ollama_fix_failed", error=str(e))
                return {"success": False, "error": str(e)}
        else:
            # Use API
            try:
                response = await self.client.post(
                    f"{self.base_url}/api/v1/fix",
                    json={
                        "code": code,
                        "errors": errors,
                        "language": language,
                        "strategy": strategy,
                    },
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error("fix_failed", error=str(e))
                return {"success": False, "error": str(e)}

    async def close(self):
        """Close HTTP clients"""
        await self.client.aclose()
        if self.ollama:
            await self.ollama.close()


async def process_file(
    file_path: Path,
    language: str,
    scanner: ErrorScanner,
    fix_client: CodeFixClient,
    dry_run: bool = False,
    strategy: str = "minimal",
    use_deep_analysis: bool = False,
) -> dict[str, Any]:
    """Process a single file"""
    logger.info("processing_file", file=str(file_path), language=language)

    # Read file
    try:
        with open(file_path, encoding="utf-8") as f:
            original_code = f.read()
    except Exception as e:
        logger.error("read_failed", file=str(file_path), error=str(e))
        return {"success": False, "error": f"Failed to read file: {e}"}

    # First, scan for basic syntax errors
    if language == "python":
        syntax_errors = scanner.scan_python_file(file_path)
    elif language == "dart":
        syntax_errors = scanner.scan_dart_file(file_path)
    else:
        return {"success": False, "error": f"Unsupported language: {language}"}

    # If using Ollama and deep analysis is enabled, analyze even if no syntax errors
    if use_deep_analysis and fix_client.use_ollama and fix_client.ollama:
        logger.info("deep_analysis", file=str(file_path))

        # Use Ollama to analyze for all types of issues
        analysis_result = await fix_client.analyze_code(original_code, language, str(file_path))

        if analysis_result.get("success"):
            ollama_issues = analysis_result.get("data", {}).get("issues", [])

            # Combine syntax errors with Ollama-detected issues
            all_errors = syntax_errors + ollama_issues

            if not all_errors:
                logger.info("no_issues_found", file=str(file_path))
                return {"success": True, "action": "skipped", "reason": "no_issues"}

            logger.info("issues_found", file=str(file_path), count=len(all_errors))
            errors = all_errors
        else:
            # Fall back to syntax errors only
            errors = syntax_errors
    else:
        errors = syntax_errors

    if not errors:
        logger.info("no_errors_found", file=str(file_path))
        return {"success": True, "action": "skipped", "reason": "no_errors"}

    logger.info("errors_found", file=str(file_path), count=len(errors))

    # Fix errors using agent (with Ollama if enabled)
    result = await fix_client.fix_code(original_code, errors, language, strategy)

    if not result.get("success"):
        logger.error("fix_failed", file=str(file_path), error=result.get("error"))
        return result

    # Get fixed code
    fixed_code = result.get("data", {}).get("fixed_code")
    if not fixed_code:
        logger.warning("no_fixed_code", file=str(file_path))
        return {"success": False, "error": "No fixed code returned"}

    # Write fixed code
    if not dry_run:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(fixed_code)
            logger.info("file_fixed", file=str(file_path))
        except Exception as e:
            logger.error("write_failed", file=str(file_path), error=str(e))
            return {"success": False, "error": f"Failed to write file: {e}"}
    else:
        logger.info("dry_run_skip_write", file=str(file_path))

    return {
        "success": True,
        "action": "fixed",
        "errors_fixed": len(errors),
        "confidence": result.get("confidence"),
    }


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Batch fix code errors using Ollama DeepSeek-Coder")
    parser.add_argument(
        "--language",
        choices=["python", "dart", "all"],
        default="all",
        help="Language to process (default: all)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Analyze only, don't modify files",
    )
    parser.add_argument(
        "--path",
        type=str,
        default=None,
        help="Specific path to process (default: entire project)",
    )
    parser.add_argument(
        "--exclude",
        type=str,
        nargs="+",
        default=["node_modules", ".git", "venv", "build", "dist", ".dart_tool", "__pycache__"],
        help="Directories to exclude",
    )
    parser.add_argument(
        "--use-api",
        action="store_true",
        help="Use code-fix-agent API instead of Ollama",
    )
    parser.add_argument(
        "--ollama-url",
        type=str,
        default=OLLAMA_URL,
        help=f"Ollama API URL (default: {OLLAMA_URL})",
    )
    parser.add_argument(
        "--ollama-model",
        type=str,
        default=OLLAMA_MODEL,
        help=f"Ollama model to use (default: {OLLAMA_MODEL})",
    )
    parser.add_argument(
        "--strategy",
        choices=["minimal", "comprehensive", "refactor"],
        default="minimal",
        help="Fix strategy (default: minimal)",
    )
    parser.add_argument(
        "--deep-analysis",
        action="store_true",
        help="Use Ollama for comprehensive analysis (logic, types, security, performance) even when no syntax errors",
    )

    args = parser.parse_args()

    # Configure logging
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(),
        ]
    )

    use_ollama = not args.use_api

    logger.info(
        "batch_fix_started",
        language=args.language,
        dry_run=args.dry_run,
        project_root=str(PROJECT_ROOT),
        use_ollama=use_ollama,
        ollama_model=args.ollama_model if use_ollama else None,
        strategy=args.strategy,
        deep_analysis=args.deep_analysis,
    )

    # Initialize scanner and client
    scanner = ErrorScanner(args.language)
    fix_client = CodeFixClient(
        CODE_FIX_AGENT_URL,
        use_ollama=use_ollama,
        ollama_url=args.ollama_url,
        ollama_model=args.ollama_model,
    )

    # Determine search path
    search_path = Path(args.path) if args.path else PROJECT_ROOT

    # Find files
    files_to_process = []
    languages = ["python", "dart"] if args.language == "all" else [args.language]

    for language in languages:
        if language == "python":
            pattern = "**/*.py"
        elif language == "dart":
            pattern = "**/*.dart"
        else:
            continue

        for file_path in search_path.glob(pattern):
            # Skip excluded directories
            if any(excluded in file_path.parts for excluded in args.exclude):
                continue

            files_to_process.append((file_path, language))

    logger.info("files_found", count=len(files_to_process))

    # Process files
    results = {
        "total": len(files_to_process),
        "fixed": 0,
        "skipped": 0,
        "failed": 0,
    }

    for file_path, language in files_to_process:
        result = await process_file(
            file_path,
            language,
            scanner,
            fix_client,
            args.dry_run,
            args.strategy,
            args.deep_analysis,
        )

        if result.get("success"):
            if result.get("action") == "fixed":
                results["fixed"] += 1
            else:
                results["skipped"] += 1
        else:
            results["failed"] += 1

    # Cleanup
    await fix_client.close()

    # Summary
    logger.info(
        "batch_fix_completed",
        total=results["total"],
        fixed=results["fixed"],
        skipped=results["skipped"],
        failed=results["failed"],
        dry_run=args.dry_run,
    )

    print("\n" + "=" * 60)
    print("BATCH FIX SUMMARY - Powered by Ollama DeepSeek-Coder" if use_ollama else "BATCH FIX SUMMARY")
    print("=" * 60)
    print(f"Total files scanned: {results['total']}")
    print(f"Files fixed: {results['fixed']}")
    print(f"Files skipped (no errors): {results['skipped']}")
    print(f"Files failed: {results['failed']}")
    if use_ollama:
        print(f"\n🤖 Using Ollama with {args.ollama_model}")
    if args.dry_run:
        print("\n⚠️  DRY RUN MODE - No files were modified")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
