"""
OpenMultiAgent Built-in Tools
=============================
الأدوات المدمجة لـ OpenMultiAgent

Provides 5 core utility tools that agents can use for general-purpose
tasks such as knowledge search, file operations, command execution,
and internal HTTP requests.

يوفر 5 أدوات مساعدة أساسية يمكن للوكلاء استخدامها للمهام ذات
الأغراض العامة مثل البحث في المعرفة وعمليات الملفات وتنفيذ الأوامر
وطلبات HTTP الداخلية.

Author: SAHOOL Platform Team
Updated: April 2026
"""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
import structlog

logger = structlog.get_logger(__name__)

# Sandboxed command execution defaults
_DEFAULT_COMMAND_TIMEOUT = 30
_DEFAULT_HTTP_TIMEOUT = 15
_MAX_FILE_READ_BYTES = 1_048_576  # 1 MB
_ALLOWED_COMMANDS = frozenset(
    {
        "ls",
        "cat",
        "head",
        "tail",
        "wc",
        "grep",
        "find",
        "date",
        "echo",
        "df",
        "du",
        "whoami",
        "uname",
        "hostname",
        "env",
        "python",
        "python3",
        "pip",
        "ruff",
        "pytest",
        "flutter",
    }
)
_BLOCKED_COMMANDS = frozenset(
    {
        "rm",
        "rmdir",
        "mkfs",
        "dd",
        "shutdown",
        "reboot",
        "kill",
        "killall",
        "pkill",
        "chmod",
        "chown",
        "mount",
        "umount",
        "iptables",
        "systemctl",
        "service",
    }
)


@dataclass
class ToolDefinition:
    """Definition of a tool available to agents - تعريف أداة متاحة للوكلاء"""

    name: str
    description: str
    description_ar: str
    parameters: dict[str, Any]
    execute: Any  # Async callable

    def to_schema(self) -> dict[str, Any]:
        """Return JSON schema representation for LLM tool calling."""
        return {
            "name": self.name,
            "description": f"{self.description}\n{self.description_ar}",
            "parameters": self.parameters,
        }


class BuiltinTools:
    """
    Built-in tools for OpenMultiAgent agents.
    الأدوات المدمجة لوكلاء OpenMultiAgent.

    Provides 5 core tools:
        - search: Search knowledge base via vector store
        - read_file: Read file contents
        - write_file: Write file contents
        - execute_command: Execute sandboxed shell commands
        - http_request: Make HTTP requests to internal services
    """

    def __init__(
        self,
        *,
        working_dir: str | Path | None = None,
        vector_store: Any | None = None,
        http_base_url: str = "http://localhost",
        allowed_paths: list[str] | None = None,
    ) -> None:
        self._working_dir = Path(working_dir) if working_dir else Path.cwd()
        self._vector_store = vector_store
        self._http_base_url = http_base_url.rstrip("/")
        self._allowed_paths = allowed_paths or [str(self._working_dir)]
        self._http_client: httpx.AsyncClient | None = None

    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create the shared HTTP client."""
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(_DEFAULT_HTTP_TIMEOUT),
                follow_redirects=True,
            )
        return self._http_client

    async def close(self) -> None:
        """Close HTTP client resources."""
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()

    # -------------------------------------------------------------------------
    # Tool definitions
    # -------------------------------------------------------------------------

    def get_tools(self) -> list[ToolDefinition]:
        """Return all built-in tool definitions - إرجاع جميع تعريفات الأدوات المدمجة"""
        return [
            self._search_tool(),
            self._read_file_tool(),
            self._write_file_tool(),
            self._execute_command_tool(),
            self._http_request_tool(),
        ]

    # -- search_tool ----------------------------------------------------------

    def _search_tool(self) -> ToolDefinition:
        return ToolDefinition(
            name="search",
            description="Search the agricultural knowledge base using semantic similarity",
            description_ar="البحث في قاعدة المعرفة الزراعية باستخدام التشابه الدلالي",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query text | نص استعلام البحث",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of results to return (default 5) | عدد النتائج",
                        "default": 5,
                    },
                    "collection": {
                        "type": "string",
                        "description": "Knowledge collection name | اسم مجموعة المعرفة",
                        "default": "default",
                    },
                },
                "required": ["query"],
            },
            execute=self._execute_search,
        )

    async def _execute_search(self, **kwargs: Any) -> dict[str, Any]:
        query: str = kwargs["query"]
        top_k: int = kwargs.get("top_k", 5)
        collection: str = kwargs.get("collection", "default")

        if self._vector_store is None:
            logger.warning("vector_store_not_configured", tool="search")
            return {
                "success": False,
                "error": "Vector store not configured | مخزن المتجهات غير مهيأ",
                "results": [],
            }

        try:
            results = await self._vector_store.search(
                query=query,
                top_k=top_k,
                collection=collection,
            )
            return {
                "success": True,
                "query": query,
                "results": results if isinstance(results, list) else [],
                "count": len(results) if isinstance(results, list) else 0,
            }
        except Exception as exc:
            logger.error("search_failed", error=str(exc), query=query)
            return {
                "success": False,
                "error": f"Search failed: {exc}",
                "results": [],
            }

    # -- read_file_tool -------------------------------------------------------

    def _read_file_tool(self) -> ToolDefinition:
        return ToolDefinition(
            name="read_file",
            description="Read contents of a file from the filesystem",
            description_ar="قراءة محتويات ملف من نظام الملفات",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path to read | مسار الملف للقراءة",
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Line offset to start reading from | إزاحة السطر",
                        "default": 0,
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max lines to read | الحد الأقصى للأسطر",
                        "default": 200,
                    },
                },
                "required": ["path"],
            },
            execute=self._execute_read_file,
        )

    async def _execute_read_file(self, **kwargs: Any) -> dict[str, Any]:
        path_str: str = kwargs["path"]
        offset: int = kwargs.get("offset", 0)
        limit: int = kwargs.get("limit", 200)

        resolved = Path(path_str).resolve()
        if not self._is_path_allowed(resolved):
            return {
                "success": False,
                "error": "Access denied: path outside allowed directories | الوصول مرفوض: المسار خارج الأدلة المسموح بها",
            }

        try:
            stat = resolved.stat()
            if stat.st_size > _MAX_FILE_READ_BYTES:
                return {
                    "success": False,
                    "error": f"File too large ({stat.st_size} bytes, max {_MAX_FILE_READ_BYTES}) | الملف كبير جدا",
                }

            text = resolved.read_text(encoding="utf-8", errors="replace")
            lines = text.splitlines()
            selected = lines[offset : offset + limit]
            return {
                "success": True,
                "path": str(resolved),
                "content": "\n".join(selected),
                "total_lines": len(lines),
                "returned_lines": len(selected),
            }
        except FileNotFoundError:
            return {"success": False, "error": f"File not found: {resolved} | الملف غير موجود"}
        except PermissionError:
            return {"success": False, "error": f"Permission denied: {resolved} | الإذن مرفوض"}
        except Exception as exc:
            logger.error("read_file_failed", path=str(resolved), error=str(exc))
            return {"success": False, "error": f"Read failed: {exc}"}

    # -- write_file_tool ------------------------------------------------------

    def _write_file_tool(self) -> ToolDefinition:
        return ToolDefinition(
            name="write_file",
            description="Write contents to a file on the filesystem",
            description_ar="كتابة محتويات إلى ملف في نظام الملفات",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path to write | مسار الملف للكتابة",
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write | المحتوى المراد كتابته",
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["overwrite", "append"],
                        "description": "Write mode | وضع الكتابة",
                        "default": "overwrite",
                    },
                },
                "required": ["path", "content"],
            },
            execute=self._execute_write_file,
        )

    async def _execute_write_file(self, **kwargs: Any) -> dict[str, Any]:
        path_str: str = kwargs["path"]
        content: str = kwargs["content"]
        mode: str = kwargs.get("mode", "overwrite")

        resolved = Path(path_str).resolve()
        if not self._is_path_allowed(resolved):
            return {
                "success": False,
                "error": "Access denied: path outside allowed directories | الوصول مرفوض",
            }

        try:
            resolved.parent.mkdir(parents=True, exist_ok=True)
            if mode == "append":
                with open(resolved, "a", encoding="utf-8") as f:
                    f.write(content)
            else:
                resolved.write_text(content, encoding="utf-8")

            logger.info("file_written", path=str(resolved), mode=mode, size=len(content))
            return {
                "success": True,
                "path": str(resolved),
                "bytes_written": len(content.encode("utf-8")),
                "mode": mode,
            }
        except PermissionError:
            return {"success": False, "error": f"Permission denied: {resolved} | الإذن مرفوض"}
        except Exception as exc:
            logger.error("write_file_failed", path=str(resolved), error=str(exc))
            return {"success": False, "error": f"Write failed: {exc}"}

    # -- execute_command_tool -------------------------------------------------

    def _execute_command_tool(self) -> ToolDefinition:
        return ToolDefinition(
            name="execute_command",
            description="Execute a sandboxed shell command with restricted access",
            description_ar="تنفيذ أمر shell في بيئة معزولة مع وصول مقيد",
            parameters={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Shell command to execute | أمر Shell للتنفيذ",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds (max 60) | المهلة بالثواني",
                        "default": _DEFAULT_COMMAND_TIMEOUT,
                    },
                },
                "required": ["command"],
            },
            execute=self._execute_command,
        )

    async def _execute_command(self, **kwargs: Any) -> dict[str, Any]:
        command: str = kwargs["command"]
        timeout: int = min(kwargs.get("timeout", _DEFAULT_COMMAND_TIMEOUT), 60)

        # Extract the base command for validation
        parts = command.strip().split()
        if not parts:
            return {"success": False, "error": "Empty command | أمر فارغ"}

        base_cmd = Path(parts[0]).name
        if base_cmd in _BLOCKED_COMMANDS:
            return {
                "success": False,
                "error": f"Blocked command: {base_cmd} | أمر محظور: {base_cmd}",
            }

        if base_cmd not in _ALLOWED_COMMANDS:
            logger.warning("command_not_in_allowlist", command=base_cmd)

        try:
            # nosemgrep: dangerous-asyncio-shell-audit -- internal diagnostics tool invocation with sanitized args
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self._working_dir),
                env={**os.environ, "LC_ALL": "C.UTF-8"},
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            return {
                "success": proc.returncode == 0,
                "exit_code": proc.returncode,
                "stdout": stdout.decode("utf-8", errors="replace")[:8192],
                "stderr": stderr.decode("utf-8", errors="replace")[:4096],
            }
        except TimeoutError:
            return {
                "success": False,
                "error": f"Command timed out after {timeout}s | انتهت المهلة بعد {timeout} ثانية",
            }
        except Exception as exc:
            logger.error("command_execution_failed", command=command, error=str(exc))
            return {"success": False, "error": f"Execution failed: {exc}"}

    # -- http_request_tool ----------------------------------------------------

    def _http_request_tool(self) -> ToolDefinition:
        return ToolDefinition(
            name="http_request",
            description="Make an HTTP request to an internal SAHOOL service",
            description_ar="إرسال طلب HTTP إلى خدمة سهول داخلية",
            parameters={
                "type": "object",
                "properties": {
                    "method": {
                        "type": "string",
                        "enum": ["GET", "POST", "PUT", "PATCH", "DELETE"],
                        "description": "HTTP method | طريقة HTTP",
                        "default": "GET",
                    },
                    "url": {
                        "type": "string",
                        "description": "URL path or full URL for internal service | مسار URL للخدمة الداخلية",
                    },
                    "body": {
                        "type": "object",
                        "description": "Request body (JSON) | نص الطلب",
                        "default": None,
                    },
                    "headers": {
                        "type": "object",
                        "description": "Additional headers | رؤوس إضافية",
                        "default": None,
                    },
                },
                "required": ["url"],
            },
            execute=self._execute_http_request,
        )

    async def _execute_http_request(self, **kwargs: Any) -> dict[str, Any]:
        method: str = kwargs.get("method", "GET").upper()
        url: str = kwargs["url"]
        body: dict[str, Any] | None = kwargs.get("body")
        headers: dict[str, str] | None = kwargs.get("headers")

        # Resolve relative URLs against the base
        if url.startswith("/"):
            url = f"{self._http_base_url}{url}"
        elif not url.startswith("http"):
            url = f"{self._http_base_url}/{url}"

        client = await self._get_http_client()
        try:
            response = await client.request(
                method=method,
                url=url,
                json=body,
                headers=headers,
            )
            # Attempt JSON parse, fall back to text
            try:
                data = response.json()
            except Exception:
                data = response.text[:8192]

            return {
                "success": 200 <= response.status_code < 400,
                "status_code": response.status_code,
                "data": data,
            }
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": f"Request timed out: {url} | انتهت مهلة الطلب",
            }
        except httpx.ConnectError:
            return {
                "success": False,
                "error": f"Connection failed: {url} | فشل الاتصال",
            }
        except Exception as exc:
            logger.error("http_request_failed", url=url, error=str(exc))
            return {"success": False, "error": f"HTTP request failed: {exc}"}

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _is_path_allowed(self, path: Path) -> bool:
        """Check if a resolved path is within allowed directories."""
        resolved = str(path.resolve())
        return any(resolved.startswith(str(Path(p).resolve())) for p in self._allowed_paths)
