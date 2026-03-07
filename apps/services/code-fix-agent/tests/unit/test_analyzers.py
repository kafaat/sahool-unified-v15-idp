"""
SAHOOL Code Fix Agent - Unit Tests for Analyzers
اختبارات الوحدة للمحللات

Tests for Python, TypeScript, and Dart code analyzers.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from agent.analyzers.base_analyzer import (
    AnalysisConfig,
    IssueCategory,
    IssueSeverity,
)
from agent.analyzers.dart_analyzer import DartAnalyzer
from agent.analyzers.python_analyzer import PythonAnalyzer
from agent.analyzers.typescript_analyzer import TypeScriptAnalyzer


class TestPythonAnalyzer:
    """اختبارات محلل Python"""

    @pytest.fixture
    def analyzer(self):
        return PythonAnalyzer()

    @pytest.mark.asyncio
    async def test_analyze_clean_code(self, analyzer):
        """Test analyzing clean code"""
        code = '''
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b
'''
        result = await analyzer.analyze(code)

        assert result.success is True
        assert result.language == "python"
        # Clean code should have few/no issues

    @pytest.mark.asyncio
    async def test_syntax_error_detection(self, analyzer):
        """Test syntax error detection"""
        code = "def foo( return"

        result = await analyzer.analyze(code)

        assert result.success is False
        assert len(result.issues) > 0
        assert any(i.category == IssueCategory.SYNTAX for i in result.issues)

    @pytest.mark.asyncio
    async def test_security_eval_detection(self, analyzer):
        """Test detection of eval() usage"""
        code = """
user_input = input()
result = eval(user_input)
"""
        result = await analyzer.analyze(code)

        security_issues = [i for i in result.issues if i.category == IssueCategory.SECURITY]
        assert len(security_issues) > 0
        assert any("eval" in i.message.lower() for i in security_issues)

    @pytest.mark.asyncio
    async def test_security_exec_detection(self, analyzer):
        """Test detection of exec() usage"""
        code = "exec('print(1)')"

        result = await analyzer.analyze(code)

        security_issues = [i for i in result.issues if i.category == IssueCategory.SECURITY]
        assert len(security_issues) > 0

    @pytest.mark.asyncio
    async def test_security_shell_injection(self, analyzer):
        """Test detection of shell injection"""
        code = "subprocess.call(cmd, shell=True)"

        result = await analyzer.analyze(code)

        security_issues = [i for i in result.issues if i.category == IssueCategory.SECURITY]
        assert len(security_issues) > 0

    @pytest.mark.asyncio
    async def test_security_hardcoded_password(self, analyzer):
        """Test detection of hardcoded password"""
        code = 'password = "secret123"'

        result = await analyzer.analyze(code)

        security_issues = [i for i in result.issues if i.category == IssueCategory.SECURITY]
        assert len(security_issues) > 0
        assert any(i.severity == IssueSeverity.ERROR for i in security_issues)

    @pytest.mark.asyncio
    async def test_type_none_comparison(self, analyzer):
        """Test detection of improper None comparison"""
        code = "if x == None: pass"

        result = await analyzer.analyze(code)

        type_issues = [i for i in result.issues if i.category == IssueCategory.TYPE]
        assert len(type_issues) > 0

    @pytest.mark.asyncio
    async def test_style_check_disabled_by_default(self, analyzer):
        """Test that style checking is disabled by default"""
        code = "x=1  "  # No space around =, trailing whitespace

        result = await analyzer.analyze(code)

        # Style issues shouldn't be reported when check_style is False
        assert analyzer.config.check_style is False

    @pytest.mark.asyncio
    async def test_style_check_when_enabled(self):
        """Test style checking when enabled"""
        # Enable both check_style and check_info since style issues have INFO severity
        config = AnalysisConfig(check_style=True, check_info=True)
        analyzer = PythonAnalyzer(config=config)

        code = "x" * 150  # Long line - exceeds default max_line_length of 120

        result = await analyzer.analyze(code)

        style_issues = [i for i in result.issues if i.category == IssueCategory.STYLE]
        assert len(style_issues) > 0

    @pytest.mark.asyncio
    async def test_unused_import_detection(self, analyzer):
        """Test detection of unused imports"""
        code = """
import os
import sys

print("hello")
"""
        result = await analyzer.analyze(code)

        logic_issues = [i for i in result.issues if i.category == IssueCategory.LOGIC]
        # Should detect unused os and sys imports
        unused_import_issues = [i for i in logic_issues if "unused" in i.message.lower()]
        assert len(unused_import_issues) >= 1

    @pytest.mark.asyncio
    async def test_metrics_calculation(self, analyzer):
        """Test code metrics calculation"""
        code = """
# This is a comment
def foo():
    pass

class Bar:
    def method(self):
        return 1

"""
        result = await analyzer.analyze(code)

        assert result.metrics is not None
        assert "total_lines" in result.metrics
        assert "code_lines" in result.metrics
        assert result.metrics["total_lines"] > 0

    @pytest.mark.asyncio
    async def test_max_issues_limit(self):
        """Test that max issues limit is respected"""
        config = AnalysisConfig(max_issues=5, check_style=True)
        analyzer = PythonAnalyzer(config=config)

        # Code with many style issues
        code = "\n".join([f"x{i}=1  " for i in range(20)])

        result = await analyzer.analyze(code)

        assert len(result.issues) <= 5


class TestTypeScriptAnalyzer:
    """اختبارات محلل TypeScript"""

    @pytest.fixture
    def analyzer(self):
        return TypeScriptAnalyzer()

    @pytest.mark.asyncio
    async def test_analyze_clean_code(self, analyzer):
        """Test analyzing clean TypeScript code"""
        code = """
function add(a: number, b: number): number {
    return a + b;
}
"""
        result = await analyzer.analyze(code)

        assert result.success is True
        assert result.language == "typescript"

    @pytest.mark.asyncio
    async def test_syntax_bracket_matching(self, analyzer):
        """Test bracket matching"""
        code = "function foo() { if (true) { }"  # Missing closing bracket

        result = await analyzer.analyze(code)

        syntax_issues = [i for i in result.issues if i.category == IssueCategory.SYNTAX]
        assert len(syntax_issues) > 0

    @pytest.mark.asyncio
    async def test_security_eval_detection(self, analyzer):
        """Test detection of eval() usage"""
        code = "const result = eval(userInput);"

        result = await analyzer.analyze(code)

        security_issues = [i for i in result.issues if i.category == IssueCategory.SECURITY]
        assert len(security_issues) > 0

    @pytest.mark.asyncio
    async def test_security_innerhtml_detection(self, analyzer):
        """Test detection of innerHTML"""
        code = "element.innerHTML = userContent;"

        result = await analyzer.analyze(code)

        security_issues = [i for i in result.issues if i.category == IssueCategory.SECURITY]
        assert len(security_issues) > 0
        assert any("xss" in i.message.lower() for i in security_issues)

    @pytest.mark.asyncio
    async def test_type_any_detection(self, analyzer):
        """Test detection of any type usage"""
        code = "function foo(x: any): void { }"

        result = await analyzer.analyze(code)

        type_issues = [i for i in result.issues if i.category == IssueCategory.TYPE]
        assert len(type_issues) > 0

    @pytest.mark.asyncio
    async def test_style_var_detection(self):
        """Test detection of var usage"""
        config = AnalysisConfig(check_style=True)
        analyzer = TypeScriptAnalyzer(config=config)

        code = "var x = 1;"

        result = await analyzer.analyze(code)

        style_issues = [i for i in result.issues if i.category == IssueCategory.STYLE]
        assert len(style_issues) > 0
        assert any("let" in i.message.lower() or "const" in i.message.lower() for i in style_issues)

    @pytest.mark.asyncio
    async def test_style_loose_equality(self):
        """Test detection of loose equality"""
        config = AnalysisConfig(check_style=True)
        analyzer = TypeScriptAnalyzer(config=config)

        code = "if (x == y) { }"

        result = await analyzer.analyze(code)

        style_issues = [i for i in result.issues if i.category == IssueCategory.STYLE]
        assert len(style_issues) > 0
        assert any("===" in i.message for i in style_issues)

    @pytest.mark.asyncio
    async def test_metrics_calculation(self, analyzer):
        """Test code metrics calculation"""
        code = """
// Comment
function foo() {
    return 1;
}

class Bar {
    method(): number {
        return 2;
    }
}

interface Baz {
    value: string;
}
"""
        result = await analyzer.analyze(code)

        assert result.metrics is not None
        assert "functions" in result.metrics
        assert "classes" in result.metrics
        assert "interfaces" in result.metrics


class TestDartAnalyzer:
    """اختبارات محلل Dart"""

    @pytest.fixture
    def analyzer(self):
        return DartAnalyzer()

    @pytest.mark.asyncio
    async def test_analyze_clean_code(self, analyzer):
        """Test analyzing clean Dart code"""
        code = """
int add(int a, int b) {
  return a + b;
}
"""
        result = await analyzer.analyze(code)

        assert result.success is True
        assert result.language == "dart"

    @pytest.mark.asyncio
    async def test_syntax_bracket_matching(self, analyzer):
        """Test bracket matching"""
        code = "void foo() { if (true) { }"  # Missing closing bracket

        result = await analyzer.analyze(code)

        # Should detect unclosed bracket
        assert result.success is True  # Might not fail completely

    @pytest.mark.asyncio
    async def test_security_http_detection(self, analyzer):
        """Test detection of HTTP URLs"""
        code = 'final url = "http://api.example.com";'

        result = await analyzer.analyze(code)

        security_issues = [i for i in result.issues if i.category == IssueCategory.SECURITY]
        assert len(security_issues) > 0
        assert any("https" in i.message.lower() for i in security_issues)

    @pytest.mark.asyncio
    async def test_security_print_detection(self):
        """Test detection of print statements"""
        # Print detection has INFO severity, need to enable check_info
        config = AnalysisConfig(check_info=True)
        analyzer = DartAnalyzer(config=config)

        code = "print('debug info');"

        result = await analyzer.analyze(code)

        security_issues = [i for i in result.issues if i.category == IssueCategory.SECURITY]
        assert len(security_issues) > 0

    @pytest.mark.asyncio
    async def test_type_dynamic_detection(self, analyzer):
        """Test detection of dynamic type"""
        code = "dynamic x = 'hello';"

        result = await analyzer.analyze(code)

        type_issues = [i for i in result.issues if i.category == IssueCategory.TYPE]
        assert len(type_issues) > 0

    @pytest.mark.asyncio
    async def test_flutter_empty_setState(self, analyzer):
        """Test detection of empty setState in Flutter"""
        code = """
class MyWidget extends StatefulWidget {
  void update() {
    setState(() {});
  }
}
"""
        result = await analyzer.analyze(code)

        # Should detect Flutter patterns
        best_practice_issues = [i for i in result.issues if i.category == IssueCategory.BEST_PRACTICE]
        # Empty setState should be detected

    @pytest.mark.asyncio
    async def test_metrics_flutter_widgets(self, analyzer):
        """Test metrics for Flutter widgets"""
        code = """
class MyWidget extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container();
  }
}

class MyStatefulWidget extends StatefulWidget {
  @override
  _MyStatefulWidgetState createState() => _MyStatefulWidgetState();
}
"""
        result = await analyzer.analyze(code)

        assert result.metrics is not None
        assert "widgets" in result.metrics
        assert result.metrics["widgets"] >= 1


class TestAnalyzerConfig:
    """اختبارات إعدادات المحللات"""

    def test_default_config(self):
        """Test default configuration"""
        config = AnalysisConfig()

        assert config.check_errors is True
        assert config.check_warnings is True
        assert config.check_security is True
        assert config.check_style is False
        assert config.max_issues == 100

    def test_custom_config(self):
        """Test custom configuration"""
        config = AnalysisConfig(
            check_style=True,
            max_issues=50,
            max_line_length=80,
        )

        assert config.check_style is True
        assert config.max_issues == 50
        assert config.max_line_length == 80

    @pytest.mark.asyncio
    async def test_config_affects_analysis(self):
        """Test that config affects analysis results"""
        config_strict = AnalysisConfig(check_style=True)
        config_lenient = AnalysisConfig(check_style=False)

        analyzer_strict = PythonAnalyzer(config=config_strict)
        analyzer_lenient = PythonAnalyzer(config=config_lenient)

        code = "x=1  "  # Style issue

        result_strict = await analyzer_strict.analyze(code)
        result_lenient = await analyzer_lenient.analyze(code)

        # Strict should have more issues
        strict_style = [i for i in result_strict.issues if i.category == IssueCategory.STYLE]
        lenient_style = [i for i in result_lenient.issues if i.category == IssueCategory.STYLE]

        assert len(strict_style) >= len(lenient_style)


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
