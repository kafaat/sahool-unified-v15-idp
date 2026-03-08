"""
SAHOOL Code Fix Agent - AST Analysis Tools
أدوات تحليل شجرة البناء المجرد

Provides Abstract Syntax Tree analysis for:
- Code structure analysis
- Symbol extraction
- Dependency mapping
- Complexity metrics
"""

import ast
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class SymbolType(Enum):
    """أنواع الرموز"""

    FUNCTION = "function"
    ASYNC_FUNCTION = "async_function"
    CLASS = "class"
    METHOD = "method"
    VARIABLE = "variable"
    CONSTANT = "constant"
    IMPORT = "import"
    PARAMETER = "parameter"
    DECORATOR = "decorator"


class NodeType(Enum):
    """أنواع العقد"""

    MODULE = "module"
    FUNCTION_DEF = "function_def"
    ASYNC_FUNCTION_DEF = "async_function_def"
    CLASS_DEF = "class_def"
    ASSIGN = "assign"
    ANN_ASSIGN = "ann_assign"
    IMPORT = "import"
    IMPORT_FROM = "import_from"
    IF = "if"
    FOR = "for"
    WHILE = "while"
    TRY = "try"
    WITH = "with"
    CALL = "call"
    RETURN = "return"
    YIELD = "yield"
    RAISE = "raise"


@dataclass
class Symbol:
    """رمز في الكود"""

    name: str
    symbol_type: SymbolType
    line_start: int
    line_end: int
    column_start: int = 0
    column_end: int = 0
    docstring: str | None = None
    decorators: list[str] = field(default_factory=list)
    parameters: list[str] = field(default_factory=list)
    return_type: str | None = None
    parent: str | None = None
    children: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Import:
    """استيراد"""

    module: str
    names: list[str]
    alias: str | None = None
    is_from: bool = False
    line: int = 0


@dataclass
class Dependency:
    """تبعية"""

    source: str
    target: str
    dependency_type: str  # "calls", "inherits", "imports", "uses"
    line: int = 0


@dataclass
class ComplexityMetrics:
    """مقاييس التعقيد"""

    cyclomatic: int = 1
    cognitive: int = 0
    lines_of_code: int = 0
    lines_of_comments: int = 0
    blank_lines: int = 0
    halstead_volume: float = 0.0
    maintainability_index: float = 100.0


@dataclass
class ASTAnalysisResult:
    """نتيجة تحليل AST"""

    success: bool
    symbols: list[Symbol] = field(default_factory=list)
    imports: list[Import] = field(default_factory=list)
    dependencies: list[Dependency] = field(default_factory=list)
    metrics: ComplexityMetrics = field(default_factory=ComplexityMetrics)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class ASTAnalyzer:
    """
    محلل شجرة البناء المجرد
    Abstract Syntax Tree Analyzer

    Features:
    - Symbol extraction (functions, classes, variables)
    - Import analysis
    - Dependency mapping
    - Complexity metrics
    - Code quality analysis
    """

    def __init__(self):
        self._tree: ast.AST | None = None
        self._source: str = ""
        self._lines: list[str] = []

    def analyze(self, source: str, filename: str = "<string>") -> ASTAnalysisResult:
        """
        تحليل الكود
        Analyze source code

        Args:
            source: الكود المصدري
            filename: اسم الملف

        Returns:
            نتيجة التحليل
        """
        self._source = source
        self._lines = source.split("\n")

        try:
            self._tree = ast.parse(source, filename=filename)
        except SyntaxError as e:
            return ASTAnalysisResult(
                success=False,
                errors=[f"Syntax error at line {e.lineno}: {e.msg}"],
            )

        # Extract information
        symbols = self._extract_symbols()
        imports = self._extract_imports()
        dependencies = self._extract_dependencies()
        metrics = self._calculate_metrics()

        return ASTAnalysisResult(
            success=True,
            symbols=symbols,
            imports=imports,
            dependencies=dependencies,
            metrics=metrics,
        )

    def _extract_symbols(self) -> list[Symbol]:
        """استخراج الرموز"""
        symbols: list[Symbol] = []

        for node in ast.walk(self._tree):
            if isinstance(node, ast.FunctionDef):
                symbols.append(self._function_to_symbol(node, is_async=False))

            elif isinstance(node, ast.AsyncFunctionDef):
                symbols.append(self._function_to_symbol(node, is_async=True))

            elif isinstance(node, ast.ClassDef):
                symbols.append(self._class_to_symbol(node))

            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        symbols.append(
                            Symbol(
                                name=target.id,
                                symbol_type=SymbolType.CONSTANT if target.id.isupper() else SymbolType.VARIABLE,
                                line_start=node.lineno,
                                line_end=node.end_lineno or node.lineno,
                                column_start=node.col_offset,
                            )
                        )

            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name):
                    symbols.append(
                        Symbol(
                            name=node.target.id,
                            symbol_type=SymbolType.VARIABLE,
                            line_start=node.lineno,
                            line_end=node.end_lineno or node.lineno,
                            column_start=node.col_offset,
                            metadata={"annotation": ast.unparse(node.annotation) if node.annotation else None},
                        )
                    )

        return symbols

    def _function_to_symbol(self, node: ast.FunctionDef | ast.AsyncFunctionDef, is_async: bool) -> Symbol:
        """تحويل دالة إلى رمز"""
        # Get decorators
        decorators = [ast.unparse(d) if hasattr(ast, "unparse") else str(d) for d in node.decorator_list]

        # Get parameters
        params = []
        for arg in node.args.args:
            param_name = arg.arg
            if arg.annotation:
                param_name += f": {ast.unparse(arg.annotation)}"
            params.append(param_name)

        # Get return type
        return_type = None
        if node.returns:
            return_type = ast.unparse(node.returns) if hasattr(ast, "unparse") else str(node.returns)

        # Get docstring
        docstring = ast.get_docstring(node)

        # Determine if it's a method
        symbol_type = SymbolType.ASYNC_FUNCTION if is_async else SymbolType.FUNCTION
        if params and params[0].startswith("self"):
            symbol_type = SymbolType.METHOD

        return Symbol(
            name=node.name,
            symbol_type=symbol_type,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            column_start=node.col_offset,
            docstring=docstring,
            decorators=decorators,
            parameters=params,
            return_type=return_type,
        )

    def _class_to_symbol(self, node: ast.ClassDef) -> Symbol:
        """تحويل فئة إلى رمز"""
        # Get decorators
        decorators = [ast.unparse(d) if hasattr(ast, "unparse") else str(d) for d in node.decorator_list]

        # Get docstring
        docstring = ast.get_docstring(node)

        # Get base classes
        bases = [ast.unparse(b) if hasattr(ast, "unparse") else str(b) for b in node.bases]

        # Get child methods
        children = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                children.append(item.name)

        return Symbol(
            name=node.name,
            symbol_type=SymbolType.CLASS,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            column_start=node.col_offset,
            docstring=docstring,
            decorators=decorators,
            children=children,
            metadata={"bases": bases},
        )

    def _extract_imports(self) -> list[Import]:
        """استخراج الاستيرادات"""
        imports: list[Import] = []

        for node in ast.walk(self._tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(
                        Import(
                            module=alias.name,
                            names=[alias.name],
                            alias=alias.asname,
                            is_from=False,
                            line=node.lineno,
                        )
                    )

            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                names = [alias.name for alias in node.names]
                imports.append(
                    Import(
                        module=module,
                        names=names,
                        is_from=True,
                        line=node.lineno,
                    )
                )

        return imports

    def _extract_dependencies(self) -> list[Dependency]:
        """استخراج التبعيات"""
        dependencies: list[Dependency] = []

        # Track current context
        current_class: str | None = None
        current_function: str | None = None

        for node in ast.walk(self._tree):
            # Track class context
            if isinstance(node, ast.ClassDef):
                current_class = node.name

                # Inheritance dependencies
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        dependencies.append(
                            Dependency(
                                source=node.name,
                                target=base.id,
                                dependency_type="inherits",
                                line=node.lineno,
                            )
                        )

            # Track function calls
            elif isinstance(node, ast.Call):
                source = current_class or current_function or "<module>"

                if isinstance(node.func, ast.Name):
                    dependencies.append(
                        Dependency(
                            source=source,
                            target=node.func.id,
                            dependency_type="calls",
                            line=node.lineno,
                        )
                    )

                elif isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name):
                        target = f"{node.func.value.id}.{node.func.attr}"
                        dependencies.append(
                            Dependency(
                                source=source,
                                target=target,
                                dependency_type="calls",
                                line=node.lineno,
                            )
                        )

        return dependencies

    def _calculate_metrics(self) -> ComplexityMetrics:
        """حساب مقاييس التعقيد"""
        metrics = ComplexityMetrics()

        # Lines of code
        metrics.lines_of_code = len([l for l in self._lines if l.strip()])
        metrics.blank_lines = len([l for l in self._lines if not l.strip()])
        metrics.lines_of_comments = len([l for l in self._lines if l.strip().startswith("#")])

        # Cyclomatic complexity
        metrics.cyclomatic = self._calculate_cyclomatic_complexity()

        # Cognitive complexity
        metrics.cognitive = self._calculate_cognitive_complexity()

        # Maintainability index (simplified)
        if metrics.lines_of_code > 0:
            loc_factor = max(0, 171 - 5.2 * (metrics.lines_of_code**0.23))
            cc_factor = max(0, 100 - 0.23 * metrics.cyclomatic)
            metrics.maintainability_index = min(100, (loc_factor + cc_factor) / 2)

        return metrics

    def _calculate_cyclomatic_complexity(self) -> int:
        """
        حساب التعقيد السيكلوماتي
        Calculate cyclomatic complexity

        CC = E - N + 2P
        Where E = edges, N = nodes, P = connected components

        Simplified: count decision points + 1
        """
        complexity = 1  # Base complexity

        decision_nodes = (
            ast.If,
            ast.For,
            ast.While,
            ast.ExceptHandler,
            ast.With,
            ast.Assert,
            ast.comprehension,
        )

        for node in ast.walk(self._tree):
            if isinstance(node, decision_nodes):
                complexity += 1

            # Boolean operations add complexity
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1

            # Conditional expressions
            elif isinstance(node, ast.IfExp):
                complexity += 1

        return complexity

    def _calculate_cognitive_complexity(self) -> int:
        """
        حساب التعقيد المعرفي
        Calculate cognitive complexity

        Based on SonarSource's cognitive complexity metric.
        """
        complexity = 0
        nesting_level = 0

        class CognitiveVisitor(ast.NodeVisitor):
            nonlocal complexity, nesting_level

            def _increment(self, amount: int = 1) -> None:
                nonlocal complexity, nesting_level
                complexity += amount + nesting_level

            def _nesting_increment(self) -> None:
                nonlocal nesting_level
                nesting_level += 1

            def _nesting_decrement(self) -> None:
                nonlocal nesting_level
                nesting_level = max(0, nesting_level - 1)

            def visit_If(self, node: ast.If) -> None:
                self._increment()
                self._nesting_increment()
                self.generic_visit(node)
                self._nesting_decrement()

            def visit_For(self, node: ast.For) -> None:
                self._increment()
                self._nesting_increment()
                self.generic_visit(node)
                self._nesting_decrement()

            def visit_While(self, node: ast.While) -> None:
                self._increment()
                self._nesting_increment()
                self.generic_visit(node)
                self._nesting_decrement()

            def visit_Try(self, node: ast.Try) -> None:
                self._increment()
                self._nesting_increment()
                self.generic_visit(node)
                self._nesting_decrement()

            def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
                self._increment()
                self.generic_visit(node)

            def visit_BoolOp(self, node: ast.BoolOp) -> None:
                self._increment(len(node.values) - 1)
                self.generic_visit(node)

            def visit_IfExp(self, node: ast.IfExp) -> None:
                self._increment()
                self.generic_visit(node)

            def visit_Lambda(self, node: ast.Lambda) -> None:
                self._increment()
                self.generic_visit(node)

        visitor = CognitiveVisitor()
        visitor.visit(self._tree)

        return complexity

    def get_function_info(self, function_name: str) -> Symbol | None:
        """
        الحصول على معلومات دالة
        Get function information
        """
        for node in ast.walk(self._tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == function_name:
                    return self._function_to_symbol(node, is_async=isinstance(node, ast.AsyncFunctionDef))
        return None

    def get_class_info(self, class_name: str) -> Symbol | None:
        """
        الحصول على معلومات فئة
        Get class information
        """
        for node in ast.walk(self._tree):
            if isinstance(node, ast.ClassDef):
                if node.name == class_name:
                    return self._class_to_symbol(node)
        return None

    def get_call_graph(self) -> dict[str, list[str]]:
        """
        الحصول على رسم بياني للاستدعاءات
        Get call graph
        """
        call_graph: dict[str, list[str]] = {}

        class CallVisitor(ast.NodeVisitor):
            current_function: str = "<module>"

            def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
                old_func = self.current_function
                self.current_function = node.name
                if node.name not in call_graph:
                    call_graph[node.name] = []
                self.generic_visit(node)
                self.current_function = old_func

            visit_AsyncFunctionDef = visit_FunctionDef

            def visit_Call(self, node: ast.Call) -> None:
                if isinstance(node.func, ast.Name):
                    if self.current_function not in call_graph:
                        call_graph[self.current_function] = []
                    call_graph[self.current_function].append(node.func.id)
                self.generic_visit(node)

        visitor = CallVisitor()
        visitor.visit(self._tree)

        return call_graph

    def find_unused_imports(self) -> list[Import]:
        """
        البحث عن الاستيرادات غير المستخدمة
        Find unused imports
        """
        imports = self._extract_imports()
        used_names: set[str] = set()

        # Collect all used names
        for node in ast.walk(self._tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name):
                    used_names.add(node.value.id)

        # Find unused
        unused: list[Import] = []
        for imp in imports:
            if imp.is_from:
                # Check if any imported name is used
                if not any(name in used_names for name in imp.names):
                    unused.append(imp)
            else:
                # Check if module name is used
                module_name = imp.alias or imp.module.split(".")[0]
                if module_name not in used_names:
                    unused.append(imp)

        return unused

    def find_undefined_names(self) -> list[tuple[str, int]]:
        """
        البحث عن الأسماء غير المعرفة
        Find undefined names
        """
        defined: set[str] = set()
        undefined: list[tuple[str, int]] = []

        # Built-in names
        import builtins

        builtins_set = set(dir(builtins))

        # Collect definitions
        for node in ast.walk(self._tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                defined.add(node.name)
                for arg in node.args.args:
                    defined.add(arg.arg)
            elif isinstance(node, ast.ClassDef):
                defined.add(node.name)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        defined.add(target.id)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    defined.add(alias.asname or alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    defined.add(alias.asname or alias.name)

        # Find uses of undefined names
        for node in ast.walk(self._tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                if node.id not in defined and node.id not in builtins_set:
                    undefined.append((node.id, node.lineno))

        return undefined
