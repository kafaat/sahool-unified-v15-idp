"""
Real-time Code Review Service using Ollama + Multiple LLMs
خدمة مراجعة الكود في الوقت الفعلي باستخدام Ollama + نماذج متعددة

Enhanced Features / الميزات المحسنة:
- Multi-model support with automatic fallback
- GitHub PR integration
- Review caching (memory, redis, file)
- Agricultural domain-specific rules for SAHOOL
"""

import asyncio
import json
import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

import aiohttp
import uvicorn
from config.settings import Settings
from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request, status

# Shared middleware imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pydantic import BaseModel, Field
from shared.errors_py import add_request_id_middleware, setup_exception_handlers
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from .agricultural_rules import AgriculturalAnalysis, AgriculturalRulesEngine

# Local imports
from .cache import CacheBackend, create_cache_backend, generate_cache_key
from .github_integration import GitHubIntegration, PRReviewResult

# Ensure logs directory exists
Path("/app/logs").mkdir(parents=True, exist_ok=True)
Path("/app/cache").mkdir(parents=True, exist_ok=True)

# Configure logging
# Setup logging - use StreamHandler only to avoid permission issues
# The logs directory may not be writable by the non-root user
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# API Models
# ═══════════════════════════════════════════════════════════════════════════


class CodeReviewRequest(BaseModel):
    """Request model for code review"""

    code: str = Field(..., description="Code content to review")
    language: str | None = Field(None, description="Programming language")
    filename: str | None = Field(None, description="Optional filename")
    use_cache: bool = Field(True, description="Use cached review if available")
    model: str | None = Field(None, description="Specific model to use")


class FileReviewRequest(BaseModel):
    """Request model for file review"""

    file_path: str = Field(..., description="Path to file in codebase")


class PRReviewRequest(BaseModel):
    """Request model for PR review"""

    pr_number: int = Field(..., description="Pull request number")
    owner: str | None = Field(None, description="Repository owner")
    repo: str | None = Field(None, description="Repository name")
    post_comment: bool = Field(True, description="Post review as PR comment")


class ReviewResponse(BaseModel):
    """Response model for code review"""

    summary: str = Field(..., description="Summary of the review")
    critical_issues: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    security_concerns: list[str] = Field(default_factory=list)
    agricultural_issues: list[str] = Field(default_factory=list)
    score: int = Field(..., ge=0, le=100, description="Review score (0-100)")
    model_used: str | None = Field(None, description="LLM model used")
    cached: bool = Field(False, description="Whether result was from cache")


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    service: str
    ollama_connected: bool
    available_models: list[str] = []
    cache_enabled: bool = False
    github_enabled: bool = False
    version: str = "2.0.0"


class CacheStatsResponse(BaseModel):
    """Cache statistics response"""

    backend: str
    size: int | None = None
    hits: int = 0
    misses: int = 0
    hit_rate: str = "0%"


class ModelInfo(BaseModel):
    """Model information"""

    name: str
    url: str
    available: bool
    priority: int


# ═══════════════════════════════════════════════════════════════════════════
# File Watcher Handler
# ═══════════════════════════════════════════════════════════════════════════


class CodeReviewHandler(FileSystemEventHandler):
    """Handles file system events for code review"""

    def __init__(self, review_service: "CodeReviewService"):
        self.review_service = review_service
        self.settings = review_service.settings
        self.pending_reviews = set()
        self._debounce_tasks = {}

    def on_modified(self, event: FileSystemEvent):
        if event.is_directory:
            return
        file_path = Path(event.src_path)
        if self._should_review(file_path):
            self._schedule_review(file_path)

    def on_created(self, event: FileSystemEvent):
        if event.is_directory:
            return
        file_path = Path(event.src_path)
        if self._should_review(file_path):
            self._schedule_review(file_path)

    def _should_review(self, file_path: Path) -> bool:
        try:
            if file_path.stat().st_size > self.settings.max_file_size:
                return False
        except OSError:
            return False

        valid_extensions = {
            ".py",
            ".ts",
            ".tsx",
            ".js",
            ".jsx",
            ".yml",
            ".yaml",
            ".json",
            ".md",
            ".sh",
            ".dockerfile",
            ".tf",
            ".go",
            ".rs",
        }
        if file_path.suffix.lower() not in valid_extensions:
            return False

        file_str = str(file_path)
        watched_paths = [p.strip() for p in self.settings.watch_paths.split(":")]
        base_path = Path("/app/codebase")

        for watch_path in watched_paths:
            if not watch_path:
                continue
            if watch_path.startswith("/"):
                check_path = Path(watch_path)
            else:
                check_path = base_path / watch_path.lstrip("/")
            if file_str.startswith(str(check_path)):
                return True
        return False

    def _schedule_review(self, file_path: Path):
        file_str = str(file_path)

        # Cancel existing debounce task
        if file_str in self._debounce_tasks:
            self._debounce_tasks[file_str].cancel()

        # Schedule new review with debounce
        async def debounced_review():
            await asyncio.sleep(self.settings.debounce_delay)
            if file_str not in self.pending_reviews:
                self.pending_reviews.add(file_str)
                await self.review_service.review_file(file_path)
                self.pending_reviews.discard(file_str)

        try:
            loop = asyncio.get_event_loop()
            self._debounce_tasks[file_str] = loop.create_task(debounced_review())
        except RuntimeError:
            pass


# ═══════════════════════════════════════════════════════════════════════════
# Main Service Class
# ═══════════════════════════════════════════════════════════════════════════


class CodeReviewService:
    """Enhanced Code Review Service with multi-model, caching, and GitHub support"""

    def __init__(self):
        self.settings = Settings()
        self.session: aiohttp.ClientSession | None = None
        self.observer: Observer | None = None
        self.cache: CacheBackend | None = None
        self.github: GitHubIntegration | None = None
        self.agricultural_engine = AgriculturalRulesEngine(self.settings)
        self._available_models: list[tuple[str, str, bool]] = []

    async def initialize(self):
        """Initialize the service and all components"""
        self.session = aiohttp.ClientSession()

        # Initialize cache
        if self.settings.enable_cache:
            self.cache = create_cache_backend(
                backend=self.settings.cache_backend,
                redis_url=self.settings.redis_url,
                cache_path=self.settings.cache_file_path,
                max_size=self.settings.cache_max_size,
                default_ttl=self.settings.cache_ttl,
            )
            logger.info(f"Cache initialized: {self.settings.cache_backend}")

        # Initialize GitHub integration
        if self.settings.github_token:
            self.github = GitHubIntegration(
                token=self.settings.github_token,
                api_url=self.settings.github_api_url,
                webhook_secret=self.settings.github_webhook_secret,
            )
            logger.info("GitHub integration enabled")

        # Check available models
        await self._discover_models()

        logger.info("═" * 60)
        logger.info("SAHOOL Code Review Service v2.0 Initialized")
        logger.info(f"Primary Model: {self.settings.ollama_model}")
        logger.info(f"Fallback Enabled: {self.settings.enable_fallback}")
        logger.info(
            f"Cache: {self.settings.cache_backend if self.settings.enable_cache else 'disabled'}"
        )
        logger.info(f"GitHub: {'enabled' if self.github else 'disabled'}")
        logger.info(f"Agricultural Rules: {self.settings.enable_agricultural_rules}")
        logger.info("═" * 60)

    async def _discover_models(self):
        """Discover available models from Ollama"""
        self._available_models = []

        # Check primary model
        primary_available = await self._check_model_available(
            self.settings.ollama_model, self.settings.ollama_url
        )
        self._available_models.append(
            (self.settings.ollama_model, self.settings.ollama_url, primary_available)
        )

        # Check fallback models
        if self.settings.enable_fallback:
            for model, url in self.settings.get_fallback_models_list():
                available = await self._check_model_available(model, url)
                self._available_models.append((model, url, available))

        available_count = sum(1 for _, _, a in self._available_models if a)
        logger.info(f"Models discovered: {available_count}/{len(self._available_models)} available")

    async def _check_model_available(self, model: str, url: str) -> bool:
        """Check if a specific model is available"""
        try:
            async with self.session.get(
                f"{url}/api/tags", timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    models = [m.get("name", "").split(":")[0] for m in data.get("models", [])]
                    return model in models or any(model in m for m in models)
        except Exception as e:
            logger.debug(f"Model check failed for {model}@{url}: {e}")
        return False

    async def check_ollama_health(self) -> bool:
        """Check if Ollama service is available"""
        try:
            async with self.session.get(
                f"{self.settings.ollama_url}/api/tags", timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                return response.status == 200
        except Exception:
            return False

    def get_available_models(self) -> list[ModelInfo]:
        """Get list of available models"""
        return [
            ModelInfo(name=name, url=url, available=avail, priority=i)
            for i, (name, url, avail) in enumerate(self._available_models)
        ]

    async def close(self):
        """Close the service"""
        if self.session:
            await self.session.close()
        if self.observer:
            self.observer.stop()
            self.observer.join()
        if self.github:
            await self.github.close()

    async def review_code(
        self,
        code: str,
        language: str | None = None,
        filename: str | None = None,
        use_cache: bool = True,
        preferred_model: str | None = None,
    ) -> dict:
        """Review code with caching, multi-model fallback, and agricultural rules"""

        if not code.strip():
            raise ValueError("Code content cannot be empty")

        # Generate cache key
        cache_key = generate_cache_key(code, language, preferred_model)

        # Check cache first
        if use_cache and self.cache:
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                cached_result["cached"] = True
                logger.info(f"Cache hit for review: {cache_key[:8]}...")
                return cached_result

        # Determine file path for context
        if filename:
            file_path = Path(filename)
        elif language:
            file_path = Path(f"code.{language}")
        else:
            file_path = Path("code.txt")

        # Run agricultural analysis
        agri_analysis = None
        if self.settings.enable_agricultural_rules:
            agri_analysis = self.agricultural_engine.analyze(code, str(file_path))

        # Create review prompt
        prompt = self._create_review_prompt(file_path, code, language, agri_analysis)

        # Get review with fallback
        review, model_used = await self._get_review_with_fallback(prompt, preferred_model)

        if "error" in review:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Review failed: {review.get('error')}",
            )

        # Add agricultural issues
        if agri_analysis and agri_analysis.issues:
            review["agricultural_issues"] = agri_analysis.get_issue_messages()
            # Adjust score based on agricultural analysis
            review["score"] = max(
                0, min(100, review.get("score", 75) + agri_analysis.score_modifier)
            )

        review["model_used"] = model_used
        review["cached"] = False

        # Store in cache
        if self.cache:
            await self.cache.set(cache_key, review)

        return review

    def _create_review_prompt(
        self,
        file_path: Path,
        content: str,
        language: str | None = None,
        agri_analysis: AgriculturalAnalysis | None = None,
    ) -> str:
        """Create a review prompt with optional agricultural context"""
        file_ext = file_path.suffix

        if language:
            file_type = language.capitalize()
        else:
            file_type = {
                ".py": "Python",
                ".ts": "TypeScript",
                ".tsx": "TypeScript React",
                ".js": "JavaScript",
                ".jsx": "JavaScript React",
                ".yml": "YAML",
                ".yaml": "YAML",
                ".json": "JSON",
                ".md": "Markdown",
                ".sh": "Bash",
                ".dockerfile": "Dockerfile",
                ".tf": "Terraform",
                ".go": "Go",
                ".rs": "Rust",
            }.get(file_ext, "Code")

        prompt = f"""You are an expert code reviewer for SAHOOL agricultural platform. Review the following {file_type} file for:
1. Code quality and best practices
2. Security vulnerabilities
3. Performance issues
4. Docker/containerization best practices (if applicable)
5. Configuration errors
6. Potential bugs

File: {file_path}

Code:
```{file_ext[1:] if file_ext else "text"}
{content[:5000]}
```
"""
        # Add agricultural context if detected
        if agri_analysis and agri_analysis.is_agricultural_code:
            prompt += (
                agri_analysis.get_enhanced_prompt(agri_analysis)
                if hasattr(self.agricultural_engine, "get_enhanced_prompt")
                else ""
            )
            prompt += (
                f"\n\nDetected agricultural domains: {', '.join(agri_analysis.detected_domains)}\n"
            )

        prompt += """
Provide a concise review with:
- Summary (1-2 sentences)
- Critical issues (if any)
- Suggestions for improvement
- Security concerns (if any)
- Agricultural issues (if applicable to SAHOOL platform)

Format your response as JSON:
{
  "summary": "...",
  "critical_issues": [...],
  "suggestions": [...],
  "security_concerns": [...],
  "agricultural_issues": [...],
  "score": 0-100
}
"""
        return prompt

    async def _get_review_with_fallback(
        self, prompt: str, preferred_model: str | None = None
    ) -> tuple[dict, str]:
        """Get review with automatic model fallback"""

        # Build model priority list
        models_to_try = []

        if preferred_model:
            # Find preferred model in available models
            for name, url, avail in self._available_models:
                if name == preferred_model and avail:
                    models_to_try.append((name, url))
                    break

        # Add all available models in priority order
        for name, url, avail in self._available_models:
            if avail and (name, url) not in models_to_try:
                models_to_try.append((name, url))

        if not models_to_try:
            return {"error": "No models available"}, "none"

        last_error = None
        for model, url in models_to_try:
            for retry in range(self.settings.max_retries):
                try:
                    result = await self._call_ollama(prompt, model, url)
                    if "error" not in result:
                        return result, model
                    last_error = result.get("error")
                except Exception as e:
                    last_error = str(e)
                    if retry < self.settings.max_retries - 1:
                        await asyncio.sleep(self.settings.retry_delay * (retry + 1))

            if not self.settings.enable_fallback:
                break
            logger.warning(f"Model {model} failed, trying next...")

        return {"error": last_error or "All models failed"}, "none"

    async def _call_ollama(self, prompt: str, model: str, url: str) -> dict:
        """Call Ollama API"""
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.3, "top_p": 0.9, "num_predict": 2000},
            }

            async with self.session.post(
                f"{url}/api/generate", json=payload, timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_response(data.get("response", ""))
                return {"error": f"API returned status {response.status}"}

        except TimeoutError:
            return {"error": "Request timeout"}
        except Exception as e:
            return {"error": str(e)}

    def _parse_response(self, response_text: str) -> dict:
        """Parse LLM response to extract JSON"""
        try:
            # Extract JSON from markdown code blocks
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            elif "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()

            result = json.loads(response_text)
            # Ensure all expected fields exist
            result.setdefault("summary", "No summary provided")
            result.setdefault("critical_issues", [])
            result.setdefault("suggestions", [])
            result.setdefault("security_concerns", [])
            result.setdefault("agricultural_issues", [])
            result.setdefault("score", 75)
            return result

        except json.JSONDecodeError:
            return {
                "summary": response_text[:500] if response_text else "No response",
                "critical_issues": [],
                "suggestions": [],
                "security_concerns": [],
                "agricultural_issues": [],
                "score": 75,
            }

    async def review_file(self, file_path: Path):
        """Review a single file"""
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            if not content.strip():
                return

            review = await self.review_code(content, filename=str(file_path))
            self._log_review(file_path, review)

        except Exception as e:
            logger.error(f"Error reviewing {file_path}: {e}")

    def _log_review(self, file_path: Path, review: dict):
        """Log the review results"""
        if not self.settings.log_reviews_to_file:
            return

        timestamp = datetime.now().isoformat()
        log_entry = {"timestamp": timestamp, "file": str(file_path), "review": review}

        log_file = Path("/app/logs/reviews.jsonl")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

        if "error" not in review:
            score = review.get("score", "N/A")
            model = review.get("model_used", "unknown")
            summary = review.get("summary", "No summary")
            logger.info(f"📝 [{model}] Review [{score}/100] {file_path.name}: {summary[:80]}")

    # ═══════════════════════════════════════════════════════════════════════════
    # GitHub Integration Methods
    # ═══════════════════════════════════════════════════════════════════════════

    async def review_pr(
        self,
        pr_number: int,
        owner: str | None = None,
        repo: str | None = None,
        post_comment: bool = True,
    ) -> PRReviewResult:
        """Review all files in a GitHub PR"""
        if not self.github:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="GitHub integration not configured"
            )

        owner = owner or self.settings.github_repo_owner
        repo = repo or self.settings.github_repo_name

        result = PRReviewResult(pr_number, owner, repo)

        # Get PR details
        pr = await self.github.get_pr(owner, repo, pr_number)
        if not pr:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"PR #{pr_number} not found"
            )

        # Get changed files
        files = await self.github.get_pr_files(owner, repo, pr_number)
        logger.info(f"Reviewing PR #{pr_number}: {len(files)} files")

        # Review each file
        for file_info in files:
            filename = file_info.get("filename", "")
            status_code = file_info.get("status", "")

            # Skip deleted files
            if status_code == "removed":
                continue

            # Get file extension
            ext = Path(filename).suffix.lower()
            reviewable_exts = {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".yaml", ".yml"}
            if ext not in reviewable_exts:
                continue

            # Get file content
            ref = pr.get("head", {}).get("sha", "HEAD")
            content = await self.github.get_file_content(owner, repo, filename, ref)

            if content:
                try:
                    review = await self.review_code(content, filename=filename)
                    result.add_file_review(filename, review)
                except Exception as e:
                    logger.error(f"Failed to review {filename}: {e}")

        # Post comment if enabled
        if post_comment and result.file_reviews:
            comment_body = self.github.format_pr_summary(result.file_reviews)

            if (
                result.total_score < self.settings.github_comment_threshold
                or result.has_critical_issues()
            ):
                await self.github.create_pr_comment(owner, repo, pr_number, comment_body)
                logger.info(f"Posted review comment on PR #{pr_number}")

        return result

    def start_watching(self):
        """Start watching the codebase"""
        event_handler = CodeReviewHandler(self)
        self.observer = Observer()

        watch_paths = self.settings.watch_paths.split(":")
        base_path = Path("/app/codebase")

        for watch_path in watch_paths:
            watch_path = watch_path.strip()
            if not watch_path:
                continue
            full_path = Path(watch_path) if watch_path.startswith("/") else base_path / watch_path
            if full_path.exists():
                self.observer.schedule(event_handler, str(full_path), recursive=True)
                logger.info(f"👀 Watching: {full_path}")

        self.observer.start()
        logger.info("🚀 File watcher started")


# ═══════════════════════════════════════════════════════════════════════════
# FastAPI Application
# ═══════════════════════════════════════════════════════════════════════════

_service_instance: CodeReviewService | None = None


def get_service() -> CodeReviewService:
    global _service_instance
    if _service_instance is None:
        _service_instance = CodeReviewService()
    return _service_instance


@asynccontextmanager
async def lifespan(app: FastAPI):
    service = get_service()
    await service.initialize()

    if service.settings.review_on_change:
        import threading

        watch_thread = threading.Thread(target=service.start_watching, daemon=True)
        watch_thread.start()

    yield
    await service.close()


app = FastAPI(
    title="SAHOOL Code Review Service",
    description="خدمة مراجعة الكود لمنصة سهول - Enhanced with multi-model, caching, and agricultural rules",
    version="2.0.0",
    lifespan=lifespan,
)

setup_exception_handlers(app)
add_request_id_middleware(app)


# ═══════════════════════════════════════════════════════════════════════════
# API Endpoints
# ═══════════════════════════════════════════════════════════════════════════


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    service = get_service()
    ollama_ok = await service.check_ollama_health()
    models = service.get_available_models()

    return HealthResponse(
        status="healthy" if ollama_ok else "degraded",
        service="code-review-service",
        ollama_connected=ollama_ok,
        available_models=[m.name for m in models if m.available],
        cache_enabled=service.settings.enable_cache,
        github_enabled=service.github is not None,
    )


@app.get("/models", response_model=list[ModelInfo])
async def list_models():
    """List available LLM models"""
    service = get_service()
    return service.get_available_models()


@app.post("/review", response_model=ReviewResponse)
async def review_code_endpoint(request: CodeReviewRequest):
    """Review code content"""
    service = get_service()
    review = await service.review_code(
        code=request.code,
        language=request.language,
        filename=request.filename,
        use_cache=request.use_cache,
        preferred_model=request.model,
    )
    return ReviewResponse(**review)


@app.post("/review/file", response_model=ReviewResponse)
async def review_file_endpoint(request: FileReviewRequest):
    """Review a file from the codebase"""
    service = get_service()
    base_path = Path("/app/codebase")
    file_path = Path(request.file_path)

    if not file_path.is_absolute():
        file_path = base_path / file_path

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")

    try:
        file_path.relative_to(base_path)
    except ValueError:
        raise HTTPException(status_code=403, detail="File must be within codebase")

    if file_path.stat().st_size > service.settings.max_file_size:
        raise HTTPException(status_code=413, detail="File too large")

    with open(file_path, encoding="utf-8", errors="ignore") as f:
        content = f.read()

    review = await service.review_code(content, filename=str(file_path.name))
    return ReviewResponse(**review)


@app.post("/review/pr")
async def review_pr_endpoint(request: PRReviewRequest, background_tasks: BackgroundTasks):
    """Review a GitHub Pull Request"""
    service = get_service()

    if not service.github:
        raise HTTPException(status_code=400, detail="GitHub integration not configured")

    result = await service.review_pr(
        pr_number=request.pr_number,
        owner=request.owner,
        repo=request.repo,
        post_comment=request.post_comment,
    )

    return {
        "pr_number": result.pr_number,
        "files_reviewed": result.files_reviewed,
        "total_score": result.total_score,
        "conclusion": result.get_conclusion(),
        "has_critical_issues": result.has_critical_issues(),
        "file_reviews": result.file_reviews,
    }


@app.post("/webhook/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(None),
    x_github_event: str | None = Header(None),
):
    """Handle GitHub webhooks for automatic PR reviews"""
    service = get_service()

    if not service.github:
        raise HTTPException(status_code=400, detail="GitHub integration not configured")

    body = await request.body()

    # Verify signature
    if service.settings.github_webhook_secret:
        if not service.github.verify_webhook_signature(body, x_hub_signature_256 or ""):
            raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()

    # Handle PR events
    if x_github_event == "pull_request":
        action = payload.get("action")
        if action in ["opened", "synchronize"]:
            pr_number = payload.get("pull_request", {}).get("number")
            if pr_number:
                # Review PR asynchronously
                asyncio.create_task(service.review_pr(pr_number))
                return {"status": "review_started", "pr": pr_number}

    return {"status": "ignored"}


@app.get("/cache/stats", response_model=CacheStatsResponse)
async def cache_stats():
    """Get cache statistics"""
    service = get_service()
    if not service.cache:
        return CacheStatsResponse(backend="disabled")

    stats = await service.cache.stats()
    return CacheStatsResponse(**stats)


@app.post("/cache/clear")
async def clear_cache():
    """Clear the review cache"""
    service = get_service()
    if not service.cache:
        return {"status": "cache_disabled"}

    await service.cache.clear()
    return {"status": "cleared"}


# ═══════════════════════════════════════════════════════════════════════════
# Main Entry Point
# ═══════════════════════════════════════════════════════════════════════════


async def main():
    service = get_service()
    await service.initialize()

    try:
        if service.settings.review_on_change:
            import threading

            watch_thread = threading.Thread(target=service.start_watching, daemon=True)
            watch_thread.start()

        config = uvicorn.Config(
            app,
            host=service.settings.api_host,
            port=service.settings.api_port,
            log_level=service.settings.log_level.lower(),
        )
        server = uvicorn.Server(config)
        await server.serve()

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        await service.close()


if __name__ == "__main__":
    asyncio.run(main())
