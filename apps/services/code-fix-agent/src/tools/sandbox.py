"""
SAHOOL Code Fix Agent - Sandbox for Safe Code Execution
بيئة معزولة لتنفيذ الكود بأمان

Provides secure code execution environment with:
- Process isolation
- Resource limits
- Timeout enforcement
- Output capture
- Security restrictions
"""

import asyncio
import os
import resource
import signal
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class ExecutionStatus(Enum):
    """حالة التنفيذ"""

    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    MEMORY_LIMIT = "memory_limit"
    SECURITY_VIOLATION = "security_violation"
    SYNTAX_ERROR = "syntax_error"


@dataclass
class SandboxConfig:
    """
    إعدادات البيئة المعزولة
    Sandbox configuration

    Security-focused defaults for safe code execution.
    """

    # Time limits
    timeout_seconds: float = 30.0
    cpu_time_limit: int = 30  # CPU seconds

    # Memory limits
    memory_limit_mb: int = 256
    stack_limit_mb: int = 8

    # File limits
    max_file_size_mb: int = 10
    max_files: int = 100
    max_output_size: int = 1_000_000  # 1MB

    # Process limits
    max_processes: int = 1

    # Network
    allow_network: bool = False

    # Filesystem
    allow_filesystem: bool = True
    read_only_paths: list[str] = field(default_factory=list)
    writable_paths: list[str] = field(default_factory=list)
    blocked_paths: list[str] = field(
        default_factory=lambda: [
            "/etc",
            "/var",
            "/usr",
            "/bin",
            "/sbin",
            "/root",
            "/home",
            "/proc",
            "/sys",
            "/dev",
        ]
    )

    # Imports
    blocked_imports: list[str] = field(
        default_factory=lambda: [
            "os.system",
            "subprocess",
            "socket",
            "requests",
            "urllib",
            "http",
            "ftplib",
            "smtplib",
            "telnetlib",
            "pickle",
            "marshal",
            "shelve",
            "ctypes",
            "multiprocessing",
        ]
    )

    # Builtins to disable
    disabled_builtins: list[str] = field(
        default_factory=lambda: [
            "eval",
            "exec",
            "compile",
            "__import__",
            "open",
            "input",
            "breakpoint",
            "help",
            "credits",
            "license",
        ]
    )


@dataclass
class SandboxResult:
    """
    نتيجة تنفيذ الكود
    Code execution result
    """

    status: ExecutionStatus
    stdout: str = ""
    stderr: str = ""
    return_value: Any = None
    execution_time_ms: float = 0.0
    memory_used_mb: float = 0.0
    error_message: str | None = None
    error_type: str | None = None
    error_line: int | None = None
    exit_code: int | None = None


class RestrictedImporter:
    """
    مستورد مقيد للوحدات
    Restricted module importer

    Prevents importing dangerous modules.
    """

    def __init__(self, blocked_imports: list[str]):
        self.blocked_imports = set(blocked_imports)

    def find_module(self, name: str, path: Any = None) -> Any:
        """Check if module is allowed"""
        for blocked in self.blocked_imports:
            if name == blocked or name.startswith(f"{blocked}."):
                raise ImportError(f"Import of '{name}' is not allowed for security reasons")
        return None


class CodeSandbox:
    """
    بيئة معزولة لتنفيذ الكود
    Secure Code Sandbox

    Features:
    - Process isolation using subprocess
    - Resource limits (CPU, memory, time)
    - Restricted imports and builtins
    - Secure temporary directory
    - Output capture and size limits

    Usage:
        sandbox = CodeSandbox()
        result = await sandbox.execute_python("print('Hello')")
    """

    SUPPORTED_LANGUAGES = {"python", "javascript", "typescript"}

    def __init__(self, config: SandboxConfig | None = None):
        """
        تهيئة البيئة المعزولة

        Args:
            config: إعدادات البيئة المعزولة
        """
        self.config = config or SandboxConfig()
        self._temp_dir: Path | None = None

    async def execute_python(
        self,
        code: str,
        inputs: dict[str, Any] | None = None,
        capture_return: bool = True,
    ) -> SandboxResult:
        """
        تنفيذ كود Python بأمان
        Execute Python code safely

        Args:
            code: الكود المراد تنفيذه
            inputs: المدخلات (سيتم تحويلها لمتغيرات)
            capture_return: التقاط قيمة الإرجاع

        Returns:
            نتيجة التنفيذ
        """
        start_time = time.time()

        # Validate code first
        validation = self._validate_python_code(code)
        if not validation["valid"]:
            return SandboxResult(
                status=ExecutionStatus.SECURITY_VIOLATION,
                error_message=validation["error"],
                error_type="SecurityViolation",
            )

        # Create secure wrapper script
        wrapper_code = self._create_python_wrapper(code, inputs, capture_return)

        # Execute in isolated process
        result = await self._execute_in_subprocess(
            language="python",
            code=wrapper_code,
        )

        result.execution_time_ms = (time.time() - start_time) * 1000
        return result

    def _validate_python_code(self, code: str) -> dict[str, Any]:
        """
        التحقق من أمان الكود
        Validate code for security issues
        """
        import ast

        # Check for syntax errors first
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return {
                "valid": False,
                "error": f"Syntax error at line {e.lineno}: {e.msg}",
            }

        # Check for dangerous patterns
        for node in ast.walk(tree):
            # Check imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in self.config.blocked_imports:
                        return {
                            "valid": False,
                            "error": f"Import of '{alias.name}' is blocked",
                        }

            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for blocked in self.config.blocked_imports:
                    if module.startswith(blocked):
                        return {
                            "valid": False,
                            "error": f"Import from '{module}' is blocked",
                        }

            # Check for eval/exec calls
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.config.disabled_builtins:
                        return {
                            "valid": False,
                            "error": f"Use of '{node.func.id}' is not allowed",
                        }

            # Check for attribute access to dangerous modules
            elif isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name):
                    full_name = f"{node.value.id}.{node.attr}"
                    for blocked in self.config.blocked_imports:
                        if full_name.startswith(blocked):
                            return {
                                "valid": False,
                                "error": f"Access to '{full_name}' is blocked",
                            }

        return {"valid": True}

    def _create_python_wrapper(
        self,
        code: str,
        inputs: dict[str, Any] | None,
        capture_return: bool,
    ) -> str:
        """
        إنشاء wrapper آمن للكود
        Create secure wrapper for code
        """
        # Build input assignments
        input_code = ""
        if inputs:
            for key, value in inputs.items():
                # Safe serialization
                input_code += f"{key} = {repr(value)}\n"

        # Build restricted builtins
        disabled = self.config.disabled_builtins
        builtins_restriction = f"""
import builtins
_original_builtins = dict(builtins.__dict__)
for _name in {disabled}:
    if _name in builtins.__dict__:
        del builtins.__dict__[_name]
"""

        # Wrapper template
        wrapper = f"""
import sys
import json
import traceback
import resource

# Set resource limits
resource.setrlimit(resource.RLIMIT_CPU, ({self.config.cpu_time_limit}, {self.config.cpu_time_limit}))
resource.setrlimit(resource.RLIMIT_AS, ({self.config.memory_limit_mb * 1024 * 1024}, {self.config.memory_limit_mb * 1024 * 1024}))
resource.setrlimit(resource.RLIMIT_FSIZE, ({self.config.max_file_size_mb * 1024 * 1024}, {self.config.max_file_size_mb * 1024 * 1024}))
resource.setrlimit(resource.RLIMIT_NPROC, ({self.config.max_processes}, {self.config.max_processes}))

{builtins_restriction}

# Input variables
{input_code}

# User code
_result = None
_error = None
try:
{self._indent_code(code, 4)}
except Exception as e:
    _error = {{
        "type": type(e).__name__,
        "message": str(e),
        "traceback": traceback.format_exc()
    }}

# Output result
if _error:
    print("__SANDBOX_ERROR__:" + json.dumps(_error), file=sys.stderr)
"""

        if capture_return:
            wrapper += """
else:
    if '_result' in dir() and _result is not None:
        try:
            print("__SANDBOX_RETURN__:" + json.dumps(_result))
        except (TypeError, ValueError, OverflowError):
            print("__SANDBOX_RETURN__:" + repr(_result))
"""

        return wrapper

    def _indent_code(self, code: str, spaces: int) -> str:
        """إضافة مسافات بادئة للكود"""
        indent = " " * spaces
        return "\n".join(indent + line for line in code.split("\n"))

    async def _execute_in_subprocess(
        self,
        language: str,
        code: str,
    ) -> SandboxResult:
        """
        تنفيذ الكود في عملية فرعية معزولة
        Execute code in isolated subprocess
        """
        # Create temporary file
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py" if language == "python" else ".js",
            delete=False,
        ) as f:
            f.write(code)
            script_path = f.name

        try:
            # Build command
            if language == "python":
                cmd = [sys.executable, "-u", script_path]
            else:
                return SandboxResult(
                    status=ExecutionStatus.ERROR,
                    error_message=f"Language '{language}' not yet supported",
                )

            # Run process with timeout
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                preexec_fn=self._set_process_limits if sys.platform != "win32" else None,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.config.timeout_seconds,
                )
            except TimeoutError:
                process.kill()
                await process.wait()
                return SandboxResult(
                    status=ExecutionStatus.TIMEOUT,
                    error_message=f"Execution exceeded {self.config.timeout_seconds}s timeout",
                )

            # Decode output
            stdout_str = stdout.decode("utf-8", errors="replace")
            stderr_str = stderr.decode("utf-8", errors="replace")

            # Truncate if needed
            if len(stdout_str) > self.config.max_output_size:
                stdout_str = stdout_str[: self.config.max_output_size] + "\n... (output truncated)"
            if len(stderr_str) > self.config.max_output_size:
                stderr_str = stderr_str[: self.config.max_output_size] + "\n... (output truncated)"

            # Parse result
            return self._parse_execution_result(
                stdout=stdout_str,
                stderr=stderr_str,
                exit_code=process.returncode,
            )

        finally:
            # Cleanup
            try:
                os.unlink(script_path)
            except Exception:
                pass

    def _set_process_limits(self) -> None:
        """تعيين حدود العملية (Unix only)"""
        try:
            # CPU time limit
            resource.setrlimit(resource.RLIMIT_CPU, (self.config.cpu_time_limit, self.config.cpu_time_limit))

            # Memory limit
            mem_bytes = self.config.memory_limit_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))

            # File size limit
            file_bytes = self.config.max_file_size_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_FSIZE, (file_bytes, file_bytes))

            # Process limit
            resource.setrlimit(resource.RLIMIT_NPROC, (self.config.max_processes, self.config.max_processes))

        except Exception as e:
            logger.warning("failed_to_set_limits", error=str(e))

    def _parse_execution_result(
        self,
        stdout: str,
        stderr: str,
        exit_code: int | None,
    ) -> SandboxResult:
        """
        تحليل نتيجة التنفيذ
        Parse execution result
        """
        import json

        # Check for sandbox markers
        return_value = None
        error_info = None

        # Extract return value
        if "__SANDBOX_RETURN__:" in stdout:
            parts = stdout.split("__SANDBOX_RETURN__:", 1)
            stdout = parts[0]
            try:
                return_value = json.loads(parts[1].strip())
            except json.JSONDecodeError:
                return_value = parts[1].strip()

        # Extract error info
        if "__SANDBOX_ERROR__:" in stderr:
            parts = stderr.split("__SANDBOX_ERROR__:", 1)
            stderr = parts[0]
            try:
                error_info = json.loads(parts[1].strip())
            except json.JSONDecodeError:
                error_info = {"message": parts[1].strip()}

        # Determine status
        if error_info:
            return SandboxResult(
                status=ExecutionStatus.ERROR,
                stdout=stdout.strip(),
                stderr=stderr.strip(),
                error_message=error_info.get("message", "Unknown error"),
                error_type=error_info.get("type", "Exception"),
                exit_code=exit_code,
            )

        if exit_code != 0:
            # Check for specific error types
            if "MemoryError" in stderr or exit_code == -9:
                return SandboxResult(
                    status=ExecutionStatus.MEMORY_LIMIT,
                    stdout=stdout.strip(),
                    stderr=stderr.strip(),
                    error_message="Memory limit exceeded",
                    exit_code=exit_code,
                )

            return SandboxResult(
                status=ExecutionStatus.ERROR,
                stdout=stdout.strip(),
                stderr=stderr.strip(),
                error_message=stderr.strip() or "Execution failed",
                exit_code=exit_code,
            )

        return SandboxResult(
            status=ExecutionStatus.SUCCESS,
            stdout=stdout.strip(),
            stderr=stderr.strip(),
            return_value=return_value,
            exit_code=0,
        )

    async def run_tests(
        self,
        code: str,
        test_code: str,
        framework: str = "pytest",
    ) -> SandboxResult:
        """
        تشغيل اختبارات على الكود
        Run tests on code

        Args:
            code: الكود المراد اختباره
            test_code: كود الاختبارات
            framework: إطار الاختبار (pytest, unittest)

        Returns:
            نتيجة التشغيل
        """
        # Combine code and tests
        combined = f'''
# Source code
{code}

# Test code
{test_code}

# Run tests
import sys
if "{framework}" == "pytest":
    import pytest
    exit_code = pytest.main(["-v", "--tb=short", __file__])
    sys.exit(exit_code)
else:
    import unittest
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
'''

        return await self.execute_python(combined, capture_return=False)

    def cleanup(self) -> None:
        """تنظيف الموارد"""
        if self._temp_dir and self._temp_dir.exists():
            import shutil

            try:
                shutil.rmtree(self._temp_dir)
            except Exception as e:
                logger.warning("cleanup_failed", error=str(e))


class SecureSandbox(CodeSandbox):
    """
    بيئة معزولة عالية الأمان
    High-security sandbox

    Uses Docker/container isolation when available.
    Falls back to process isolation.
    """

    def __init__(self, config: SandboxConfig | None = None):
        super().__init__(config)
        self._docker_available = self._check_docker()

    def _check_docker(self) -> bool:
        """التحقق من توفر Docker"""
        try:
            result = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
        except Exception:
            return False

    async def execute_python(
        self,
        code: str,
        inputs: dict[str, Any] | None = None,
        capture_return: bool = True,
    ) -> SandboxResult:
        """
        تنفيذ كود Python مع عزل Docker إذا كان متاحاً
        Execute Python with Docker isolation if available
        """
        if self._docker_available:
            return await self._execute_in_docker(code, inputs, capture_return)
        else:
            return await super().execute_python(code, inputs, capture_return)

    async def _execute_in_docker(
        self,
        code: str,
        inputs: dict[str, Any] | None,
        capture_return: bool,
    ) -> SandboxResult:
        """
        تنفيذ في حاوية Docker
        Execute in Docker container
        """
        start_time = time.time()

        # Validate code first
        validation = self._validate_python_code(code)
        if not validation["valid"]:
            return SandboxResult(
                status=ExecutionStatus.SECURITY_VIOLATION,
                error_message=validation["error"],
            )

        # Create wrapper
        wrapper_code = self._create_python_wrapper(code, inputs, capture_return)

        # Write to temp file
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
        ) as f:
            f.write(wrapper_code)
            script_path = f.name

        try:
            # Build Docker command
            cmd = [
                "docker",
                "run",
                "--rm",
                "--network=none",  # No network
                f"--memory={self.config.memory_limit_mb}m",
                f"--cpus={self.config.cpu_time_limit / 10}",
                "--read-only",
                "--security-opt=no-new-privileges",
                "-v",
                f"{script_path}:/code/script.py:ro",
                "python:3.11-slim",
                "python",
                "-u",
                "/code/script.py",
            ]

            # Run Docker
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.config.timeout_seconds + 5,  # Extra time for Docker
                )
            except TimeoutError:
                # Kill container
                subprocess.run(["docker", "kill", str(process.pid)], capture_output=True)
                return SandboxResult(
                    status=ExecutionStatus.TIMEOUT,
                    error_message="Docker execution timeout",
                    execution_time_ms=(time.time() - start_time) * 1000,
                )

            result = self._parse_execution_result(
                stdout=stdout.decode("utf-8", errors="replace"),
                stderr=stderr.decode("utf-8", errors="replace"),
                exit_code=process.returncode,
            )
            result.execution_time_ms = (time.time() - start_time) * 1000
            return result

        finally:
            try:
                os.unlink(script_path)
            except Exception:
                pass
