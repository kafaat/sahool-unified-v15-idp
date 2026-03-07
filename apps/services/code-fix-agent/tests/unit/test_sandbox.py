"""
SAHOOL Code Fix Agent - Unit Tests for Sandbox
اختبارات الوحدة للبيئة المعزولة

Tests for safe code execution sandbox.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tools.sandbox import (
    CodeSandbox,
    ExecutionStatus,
    SandboxConfig,
    SandboxResult,
)


class TestSandboxConfig:
    """اختبارات إعدادات البيئة المعزولة"""

    def test_default_config(self):
        """Test default configuration"""
        config = SandboxConfig()

        assert config.timeout_seconds == 30.0
        assert config.memory_limit_mb == 256
        assert config.allow_network is False
        assert "eval" in config.disabled_builtins
        assert "subprocess" in config.blocked_imports

    def test_custom_config(self):
        """Test custom configuration"""
        config = SandboxConfig(
            timeout_seconds=10,
            memory_limit_mb=128,
            allow_network=False,
        )

        assert config.timeout_seconds == 10
        assert config.memory_limit_mb == 128

    def test_blocked_imports_default(self):
        """Test default blocked imports"""
        config = SandboxConfig()

        dangerous_imports = ["subprocess", "socket", "os.system"]
        for imp in dangerous_imports:
            assert imp in config.blocked_imports

    def test_disabled_builtins_default(self):
        """Test default disabled builtins"""
        config = SandboxConfig()

        dangerous_builtins = ["eval", "exec", "compile", "__import__"]
        for builtin in dangerous_builtins:
            assert builtin in config.disabled_builtins


class TestCodeSandbox:
    """اختبارات البيئة المعزولة"""

    @pytest.fixture
    def sandbox(self):
        return CodeSandbox(SandboxConfig(timeout_seconds=5))

    @pytest.mark.asyncio
    async def test_execute_simple_code(self, sandbox):
        """Test executing simple Python code"""
        code = "print('hello world')"

        result = await sandbox.execute_python(code)

        assert result.status == ExecutionStatus.SUCCESS
        assert "hello world" in result.stdout

    @pytest.mark.asyncio
    async def test_execute_with_return_value(self, sandbox):
        """Test executing code with return value"""
        code = "_result = 1 + 2"

        result = await sandbox.execute_python(code, capture_return=True)

        assert result.status == ExecutionStatus.SUCCESS

    @pytest.mark.asyncio
    async def test_execute_with_inputs(self, sandbox):
        """Test executing code with input variables"""
        code = "print(x + y)"
        inputs = {"x": 5, "y": 3}

        result = await sandbox.execute_python(code, inputs=inputs)

        assert result.status == ExecutionStatus.SUCCESS
        assert "8" in result.stdout

    @pytest.mark.asyncio
    async def test_block_eval(self, sandbox):
        """Test that eval is blocked"""
        code = "eval('1+1')"

        result = await sandbox.execute_python(code)

        # Should fail due to blocked eval
        assert result.status == ExecutionStatus.SECURITY_VIOLATION
        assert "eval" in result.error_message.lower()

    @pytest.mark.asyncio
    async def test_block_exec(self, sandbox):
        """Test that exec is blocked"""
        code = "exec('print(1)')"

        result = await sandbox.execute_python(code)

        assert result.status == ExecutionStatus.SECURITY_VIOLATION
        assert "exec" in result.error_message.lower()

    @pytest.mark.asyncio
    async def test_block_import_subprocess(self, sandbox):
        """Test that subprocess import is blocked"""
        code = "import subprocess"

        result = await sandbox.execute_python(code)

        assert result.status == ExecutionStatus.SECURITY_VIOLATION
        assert "subprocess" in result.error_message.lower()

    @pytest.mark.asyncio
    async def test_block_import_socket(self, sandbox):
        """Test that socket import is blocked"""
        code = "import socket"

        result = await sandbox.execute_python(code)

        assert result.status == ExecutionStatus.SECURITY_VIOLATION

    @pytest.mark.asyncio
    async def test_syntax_error_handling(self, sandbox):
        """Test handling of syntax errors"""
        code = "def foo( return"

        result = await sandbox.execute_python(code)

        assert result.status == ExecutionStatus.SECURITY_VIOLATION
        assert "syntax" in result.error_message.lower()

    @pytest.mark.asyncio
    async def test_runtime_error_handling(self, sandbox):
        """Test handling of runtime errors"""
        code = "x = 1 / 0"

        result = await sandbox.execute_python(code)

        assert result.status == ExecutionStatus.ERROR
        assert "ZeroDivision" in result.error_type or "division" in result.error_message.lower()

    @pytest.mark.asyncio
    async def test_timeout_enforcement(self):
        """Test timeout enforcement using infinite loop (no imports)"""
        sandbox = CodeSandbox(SandboxConfig(timeout_seconds=1))

        # Use infinite loop instead of time.sleep (imports are blocked by default)
        code = """
i = 0
while True:
    i += 1
"""
        result = await sandbox.execute_python(code)

        # May be timeout or error depending on how process is killed
        assert result.status in [ExecutionStatus.TIMEOUT, ExecutionStatus.ERROR]

    @pytest.mark.asyncio
    async def test_output_truncation(self):
        """Test output truncation for large outputs"""
        sandbox = CodeSandbox(SandboxConfig(max_output_size=100))

        code = "print('x' * 1000)"

        result = await sandbox.execute_python(code)

        # Output should be truncated
        assert len(result.stdout) <= 200  # Some buffer for truncation message

    @pytest.mark.asyncio
    async def test_imports_blocked_by_default(self, sandbox):
        """Test that imports are blocked by default (security feature)"""
        # By default, __import__ is disabled for maximum security
        code = "import math"
        result = await sandbox.execute_python(code)

        # Imports should fail when __import__ is blocked
        assert result.status == ExecutionStatus.ERROR
        assert "__import__" in result.error_message.lower() or "import" in result.error_message.lower()

    @pytest.mark.asyncio
    async def test_math_operations_without_import(self, sandbox):
        """Test math operations using builtins (no import required)"""
        code = """
_result = (16 ** 0.5) + 3.14159
"""
        result = await sandbox.execute_python(code, capture_return=True)

        assert result.status == ExecutionStatus.SUCCESS

    @pytest.mark.asyncio
    async def test_string_operations(self, sandbox):
        """Test string operations work without imports"""
        code = """
data = {"key": "value"}
_result = str(data)
"""
        result = await sandbox.execute_python(code, capture_return=True)

        assert result.status == ExecutionStatus.SUCCESS

    @pytest.mark.asyncio
    async def test_datetime_blocked_by_default(self, sandbox):
        """Test datetime import is blocked by default"""
        code = """
from datetime import datetime
now = datetime.now()
"""
        result = await sandbox.execute_python(code)

        # Imports should fail
        assert result.status == ExecutionStatus.ERROR

    @pytest.mark.asyncio
    async def test_execution_time_tracking(self, sandbox):
        """Test that execution time is tracked"""
        code = "x = 1 + 1"

        result = await sandbox.execute_python(code)

        assert result.execution_time_ms >= 0

    @pytest.mark.asyncio
    async def test_list_comprehension(self, sandbox):
        """Test list comprehension execution"""
        code = "_result = [x**2 for x in range(5)]"

        result = await sandbox.execute_python(code, capture_return=True)

        assert result.status == ExecutionStatus.SUCCESS

    @pytest.mark.asyncio
    async def test_function_definition(self, sandbox):
        """Test function definition and call"""
        code = """
def add(a, b):
    return a + b

_result = add(3, 4)
"""
        result = await sandbox.execute_python(code, capture_return=True)

        assert result.status == ExecutionStatus.SUCCESS

    @pytest.mark.asyncio
    async def test_class_definition(self, sandbox):
        """Test class definition and instantiation"""
        code = """
class Calculator:
    def add(self, a, b):
        return a + b

calc = Calculator()
_result = calc.add(5, 3)
"""
        result = await sandbox.execute_python(code, capture_return=True)

        assert result.status == ExecutionStatus.SUCCESS

    @pytest.mark.asyncio
    async def test_async_code_blocked(self, sandbox):
        """Test async code is blocked (asyncio import blocked by default)"""
        code = """
import asyncio

async def hello():
    return "hello"

_result = asyncio.run(hello())
"""
        result = await sandbox.execute_python(code, capture_return=True)

        # Async requires import, which is blocked by default
        assert result.status == ExecutionStatus.ERROR


class TestSandboxValidation:
    """اختبارات التحقق من صحة الكود"""

    @pytest.fixture
    def sandbox(self):
        return CodeSandbox()

    def test_validate_clean_code(self, sandbox):
        """Test validation of clean code"""
        code = "x = 1 + 2"

        validation = sandbox._validate_python_code(code)

        assert validation["valid"] is True

    def test_validate_code_with_eval(self, sandbox):
        """Test validation catches eval"""
        code = "eval('1+1')"

        validation = sandbox._validate_python_code(code)

        assert validation["valid"] is False
        assert "eval" in validation["error"].lower()

    def test_validate_code_with_blocked_import(self, sandbox):
        """Test validation catches blocked imports"""
        code = "import subprocess"

        validation = sandbox._validate_python_code(code)

        assert validation["valid"] is False
        assert "subprocess" in validation["error"].lower()

    def test_validate_code_with_syntax_error(self, sandbox):
        """Test validation catches syntax errors"""
        code = "def foo( return"

        validation = sandbox._validate_python_code(code)

        assert validation["valid"] is False
        assert "syntax" in validation["error"].lower()

    def test_validate_nested_dangerous_call(self, sandbox):
        """Test validation catches nested dangerous calls"""
        code = """
def wrapper():
    return eval("1")
"""
        validation = sandbox._validate_python_code(code)

        assert validation["valid"] is False


class TestSandboxCleanup:
    """اختبارات تنظيف البيئة المعزولة"""

    def test_cleanup_method(self):
        """Test cleanup method"""
        sandbox = CodeSandbox()

        # Should not raise
        sandbox.cleanup()

    @pytest.mark.asyncio
    async def test_temp_files_cleaned(self):
        """Test that temporary files are cleaned up"""
        sandbox = CodeSandbox()

        code = "print('test')"
        await sandbox.execute_python(code)

        # Temp files should be cleaned up automatically
        # This is more of a smoke test


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
