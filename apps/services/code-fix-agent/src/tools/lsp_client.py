"""
SAHOOL Code Fix Agent - LSP Client
عميل بروتوكول خادم اللغة

Language Server Protocol client for IDE integration:
- Code completion
- Go to definition
- Find references
- Hover information
- Diagnostics
"""

import asyncio
import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class LSPMessageType(Enum):
    """أنواع رسائل LSP"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"


class DiagnosticSeverity(Enum):
    """شدة التشخيص"""
    ERROR = 1
    WARNING = 2
    INFORMATION = 3
    HINT = 4


@dataclass
class Position:
    """موقع في الملف"""
    line: int
    character: int


@dataclass
class Range:
    """نطاق في الملف"""
    start: Position
    end: Position


@dataclass
class Location:
    """موقع كامل"""
    uri: str
    range: Range


@dataclass
class Diagnostic:
    """تشخيص"""
    range: Range
    severity: DiagnosticSeverity
    code: str | None = None
    source: str | None = None
    message: str = ""
    related_information: list[dict] = field(default_factory=list)


@dataclass
class CompletionItem:
    """عنصر إكمال"""
    label: str
    kind: int  # CompletionItemKind
    detail: str | None = None
    documentation: str | None = None
    insert_text: str | None = None
    text_edit: dict | None = None


@dataclass
class Hover:
    """معلومات التمرير"""
    contents: str | list[str]
    range: Range | None = None


@dataclass
class SymbolInformation:
    """معلومات الرمز"""
    name: str
    kind: int  # SymbolKind
    location: Location
    container_name: str | None = None


class LSPClient:
    """
    عميل LSP
    Language Server Protocol Client

    Provides IDE-like features:
    - Code completion
    - Go to definition
    - Find references
    - Hover documentation
    - Diagnostics

    Note: This is a simplified implementation.
    For production, use a full LSP client library.
    """

    # LSP Message IDs
    _id_counter = 0

    # Completion item kinds
    COMPLETION_KINDS = {
        "text": 1,
        "method": 2,
        "function": 3,
        "constructor": 4,
        "field": 5,
        "variable": 6,
        "class": 7,
        "interface": 8,
        "module": 9,
        "property": 10,
        "keyword": 14,
        "snippet": 15,
        "constant": 21,
    }

    # Symbol kinds
    SYMBOL_KINDS = {
        "file": 1,
        "module": 2,
        "namespace": 3,
        "package": 4,
        "class": 5,
        "method": 6,
        "property": 7,
        "field": 8,
        "constructor": 9,
        "enum": 10,
        "interface": 11,
        "function": 12,
        "variable": 13,
        "constant": 14,
    }

    def __init__(
        self,
        language: str = "python",
        workspace_root: Path | None = None,
    ):
        """
        تهيئة عميل LSP

        Args:
            language: اللغة المستهدفة
            workspace_root: جذر مساحة العمل
        """
        self.language = language
        self.workspace_root = workspace_root or Path.cwd()
        self._initialized = False
        self._server_process: asyncio.subprocess.Process | None = None
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._pending_requests: dict[int, asyncio.Future] = {}

    @classmethod
    def _next_id(cls) -> int:
        """الحصول على المعرف التالي"""
        cls._id_counter += 1
        return cls._id_counter

    async def initialize(self) -> bool:
        """
        تهيئة الاتصال بخادم اللغة
        Initialize connection to language server
        """
        logger.info("lsp_initializing", language=self.language)

        # For now, we'll use a simplified in-process analysis
        # In production, this would start an actual LSP server
        self._initialized = True

        logger.info("lsp_initialized", language=self.language)
        return True

    async def shutdown(self) -> None:
        """إيقاف الاتصال"""
        if self._server_process:
            self._server_process.terminate()
            await self._server_process.wait()

        self._initialized = False
        logger.info("lsp_shutdown")

    async def get_completions(
        self,
        document_uri: str,
        position: Position,
        content: str | None = None,
    ) -> list[CompletionItem]:
        """
        الحصول على اقتراحات الإكمال
        Get completion suggestions

        Args:
            document_uri: معرف المستند
            position: الموقع
            content: محتوى المستند

        Returns:
            قائمة اقتراحات الإكمال
        """
        if not self._initialized:
            await self.initialize()

        completions: list[CompletionItem] = []

        if self.language == "python" and content:
            completions = self._get_python_completions(content, position)

        return completions

    def _get_python_completions(
        self,
        content: str,
        position: Position,
    ) -> list[CompletionItem]:
        """الحصول على إكمالات Python"""
        completions: list[CompletionItem] = []

        try:
            # Use jedi for Python completion if available
            try:
                import jedi
                script = jedi.Script(content, path="<string>")
                jedi_completions = script.complete(
                    position.line + 1,  # jedi uses 1-indexed lines
                    position.character,
                )
                for c in jedi_completions[:50]:  # Limit results
                    kind = self.COMPLETION_KINDS.get(c.type, 1)
                    completions.append(CompletionItem(
                        label=c.name,
                        kind=kind,
                        detail=c.type,
                        documentation=c.docstring() if hasattr(c, 'docstring') else None,
                    ))
            except ImportError:
                # Fallback: basic keyword completion
                completions = self._get_basic_python_completions(content, position)

        except Exception as e:
            logger.warning("completion_error", error=str(e))

        return completions

    def _get_basic_python_completions(
        self,
        content: str,
        position: Position,
    ) -> list[CompletionItem]:
        """إكمالات Python أساسية"""
        # Python keywords
        keywords = [
            "and", "as", "assert", "async", "await", "break", "class",
            "continue", "def", "del", "elif", "else", "except", "finally",
            "for", "from", "global", "if", "import", "in", "is", "lambda",
            "None", "nonlocal", "not", "or", "pass", "raise", "return",
            "True", "False", "try", "while", "with", "yield",
        ]

        # Common builtins
        builtins = [
            "print", "len", "range", "str", "int", "float", "list",
            "dict", "set", "tuple", "bool", "type", "isinstance",
            "hasattr", "getattr", "setattr", "open", "input",
            "enumerate", "zip", "map", "filter", "sorted", "reversed",
            "sum", "min", "max", "abs", "round", "any", "all",
        ]

        completions = []

        for kw in keywords:
            completions.append(CompletionItem(
                label=kw,
                kind=self.COMPLETION_KINDS["keyword"],
                detail="keyword",
            ))

        for b in builtins:
            completions.append(CompletionItem(
                label=b,
                kind=self.COMPLETION_KINDS["function"],
                detail="builtin",
            ))

        return completions

    async def get_definition(
        self,
        document_uri: str,
        position: Position,
        content: str | None = None,
    ) -> list[Location]:
        """
        الانتقال إلى التعريف
        Go to definition

        Args:
            document_uri: معرف المستند
            position: الموقع
            content: محتوى المستند

        Returns:
            قائمة المواقع
        """
        if not self._initialized:
            await self.initialize()

        locations: list[Location] = []

        if self.language == "python" and content:
            try:
                import jedi
                script = jedi.Script(content, path="<string>")
                definitions = script.goto(
                    position.line + 1,
                    position.character,
                )
                for d in definitions:
                    if d.module_path:
                        locations.append(Location(
                            uri=f"file://{d.module_path}",
                            range=Range(
                                start=Position(d.line - 1, d.column),
                                end=Position(d.line - 1, d.column),
                            ),
                        ))
            except ImportError:
                pass
            except Exception as e:
                logger.warning("definition_error", error=str(e))

        return locations

    async def get_references(
        self,
        document_uri: str,
        position: Position,
        content: str | None = None,
        include_declaration: bool = True,
    ) -> list[Location]:
        """
        البحث عن المراجع
        Find references

        Args:
            document_uri: معرف المستند
            position: الموقع
            content: محتوى المستند
            include_declaration: تضمين التعريف

        Returns:
            قائمة المواقع
        """
        if not self._initialized:
            await self.initialize()

        locations: list[Location] = []

        if self.language == "python" and content:
            try:
                import jedi
                script = jedi.Script(content, path="<string>")
                references = script.get_references(
                    position.line + 1,
                    position.character,
                    include_builtins=False,
                )
                for ref in references:
                    if ref.module_path:
                        locations.append(Location(
                            uri=f"file://{ref.module_path}",
                            range=Range(
                                start=Position(ref.line - 1, ref.column),
                                end=Position(ref.line - 1, ref.column),
                            ),
                        ))
            except ImportError:
                pass
            except Exception as e:
                logger.warning("references_error", error=str(e))

        return locations

    async def get_hover(
        self,
        document_uri: str,
        position: Position,
        content: str | None = None,
    ) -> Hover | None:
        """
        الحصول على معلومات التمرير
        Get hover information

        Args:
            document_uri: معرف المستند
            position: الموقع
            content: محتوى المستند

        Returns:
            معلومات التمرير
        """
        if not self._initialized:
            await self.initialize()

        if self.language == "python" and content:
            try:
                import jedi
                script = jedi.Script(content, path="<string>")
                help_items = script.help(
                    position.line + 1,
                    position.character,
                )
                if help_items:
                    item = help_items[0]
                    return Hover(
                        contents=[
                            f"```python\n{item.full_name}\n```",
                            item.docstring() or "",
                        ],
                        range=Range(
                            start=Position(position.line, position.character),
                            end=Position(position.line, position.character),
                        ),
                    )
            except ImportError:
                pass
            except Exception as e:
                logger.warning("hover_error", error=str(e))

        return None

    async def get_diagnostics(
        self,
        document_uri: str,
        content: str,
    ) -> list[Diagnostic]:
        """
        الحصول على التشخيصات
        Get diagnostics

        Args:
            document_uri: معرف المستند
            content: محتوى المستند

        Returns:
            قائمة التشخيصات
        """
        if not self._initialized:
            await self.initialize()

        diagnostics: list[Diagnostic] = []

        if self.language == "python":
            diagnostics = self._get_python_diagnostics(content)

        return diagnostics

    def _get_python_diagnostics(self, content: str) -> list[Diagnostic]:
        """الحصول على تشخيصات Python"""
        diagnostics: list[Diagnostic] = []

        # Syntax check
        try:
            compile(content, "<string>", "exec")
        except SyntaxError as e:
            diagnostics.append(Diagnostic(
                range=Range(
                    start=Position(e.lineno - 1 if e.lineno else 0, e.offset or 0),
                    end=Position(e.lineno - 1 if e.lineno else 0, (e.offset or 0) + 1),
                ),
                severity=DiagnosticSeverity.ERROR,
                code="E999",
                source="python",
                message=e.msg or "Syntax error",
            ))
            return diagnostics

        # Try to use pyflakes for more diagnostics
        try:
            import pyflakes.api
            import pyflakes.messages

            # Run pyflakes
            warnings = []
            pyflakes.api.check(content, "<string>", reporter=lambda *args: warnings.append(args))

        except ImportError:
            pass

        return diagnostics

    async def get_document_symbols(
        self,
        document_uri: str,
        content: str,
    ) -> list[SymbolInformation]:
        """
        الحصول على رموز المستند
        Get document symbols

        Args:
            document_uri: معرف المستند
            content: محتوى المستند

        Returns:
            قائمة الرموز
        """
        if not self._initialized:
            await self.initialize()

        symbols: list[SymbolInformation] = []

        if self.language == "python":
            import ast

            try:
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                        symbols.append(SymbolInformation(
                            name=node.name,
                            kind=self.SYMBOL_KINDS["function"],
                            location=Location(
                                uri=document_uri,
                                range=Range(
                                    start=Position(node.lineno - 1, node.col_offset),
                                    end=Position(
                                        (node.end_lineno or node.lineno) - 1,
                                        node.end_col_offset or 0,
                                    ),
                                ),
                            ),
                        ))

                    elif isinstance(node, ast.ClassDef):
                        symbols.append(SymbolInformation(
                            name=node.name,
                            kind=self.SYMBOL_KINDS["class"],
                            location=Location(
                                uri=document_uri,
                                range=Range(
                                    start=Position(node.lineno - 1, node.col_offset),
                                    end=Position(
                                        (node.end_lineno or node.lineno) - 1,
                                        node.end_col_offset or 0,
                                    ),
                                ),
                            ),
                        ))

            except SyntaxError:
                pass

        return symbols

    async def format_document(
        self,
        document_uri: str,
        content: str,
        options: dict[str, Any] | None = None,
    ) -> str | None:
        """
        تنسيق المستند
        Format document

        Args:
            document_uri: معرف المستند
            content: محتوى المستند
            options: خيارات التنسيق

        Returns:
            المحتوى المنسق
        """
        if self.language == "python":
            try:
                import subprocess
                result = subprocess.run(
                    ["ruff", "format", "-"],
                    input=content,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if result.returncode == 0:
                    return result.stdout
            except Exception as e:
                logger.warning("format_error", error=str(e))

        return None

    async def get_code_actions(
        self,
        document_uri: str,
        range_: Range,
        content: str,
        diagnostics: list[Diagnostic] | None = None,
    ) -> list[dict[str, Any]]:
        """
        الحصول على إجراءات الكود
        Get code actions

        Args:
            document_uri: معرف المستند
            range_: النطاق
            content: محتوى المستند
            diagnostics: التشخيصات

        Returns:
            قائمة الإجراءات
        """
        actions: list[dict[str, Any]] = []

        # Add quick fix actions based on diagnostics
        if diagnostics:
            for diag in diagnostics:
                if diag.code == "E999":  # Syntax error
                    actions.append({
                        "title": "Fix syntax error",
                        "kind": "quickfix",
                        "diagnostics": [diag],
                        "isPreferred": True,
                    })

        # Add refactoring actions
        actions.extend([
            {
                "title": "Extract variable",
                "kind": "refactor.extract.variable",
            },
            {
                "title": "Extract function",
                "kind": "refactor.extract.function",
            },
            {
                "title": "Organize imports",
                "kind": "source.organizeImports",
            },
        ])

        return actions
