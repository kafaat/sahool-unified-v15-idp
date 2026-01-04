"""
Real-time Code Review Service using Ollama + DeepSeek
خدمة مراجعة الكود في الوقت الفعلي باستخدام Ollama + DeepSeek

Monitors codebase changes and provides real-time code reviews
يراقب تغييرات الكود ويقدم مراجعات في الوقت الفعلي
"""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

import aiohttp
import uvicorn
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from config.settings import Settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/code-review.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# API Models
# ═══════════════════════════════════════════════════════════════════════════

class CodeReviewRequest(BaseModel):
    """Request model for code review"""
    code: str = Field(..., description="Code content to review")
    language: str | None = Field(None, description="Programming language (e.g., python, typescript)")
    filename: str | None = Field(None, description="Optional filename for context")


class FileReviewRequest(BaseModel):
    """Request model for file review"""
    file_path: str = Field(..., description="Relative or absolute path to file in codebase")


class ReviewResponse(BaseModel):
    """Response model for code review"""
    summary: str = Field(..., description="Summary of the review")
    critical_issues: list[str] = Field(default_factory=list, description="List of critical issues")
    suggestions: list[str] = Field(default_factory=list, description="List of suggestions")
    security_concerns: list[str] = Field(default_factory=list, description="List of security concerns")
    score: int = Field(..., ge=0, le=100, description="Review score (0-100)")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    ollama_connected: bool
    version: str = "1.0.0"


class CodeReviewHandler(FileSystemEventHandler):
    """Handles file system events for code review"""

    def __init__(self, review_service: 'CodeReviewService'):
        self.review_service = review_service
        self.settings = review_service.settings
        self.pending_reviews = set()

    def on_modified(self, event: FileSystemEvent):
        """Handle file modification events"""
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        if self._should_review(file_path):
            self._schedule_review(file_path)

    def on_created(self, event: FileSystemEvent):
        """Handle file creation events"""
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        if self._should_review(file_path):
            self._schedule_review(file_path)

    def _should_review(self, file_path: Path) -> bool:
        """Check if file should be reviewed"""
        # Check file size
        try:
            if file_path.stat().st_size > self.settings.max_file_size:
                return False
        except OSError:
            return False

        # Check file extension
        valid_extensions = {'.py', '.ts', '.tsx', '.js', '.jsx', '.yml', '.yaml',
                          '.json', '.md', '.sh', '.dockerfile', '.tf', '.go', '.rs'}
        if file_path.suffix.lower() not in valid_extensions:
            return False

        # Check if in watched paths
        file_str = str(file_path)
        watched_paths = [p.strip() for p in self.settings.watch_paths.split(':')]
        base_path = Path('/app/codebase')

        for watch_path in watched_paths:
            if not watch_path:
                continue
            # Handle both absolute and relative paths
            if watch_path.startswith('/'):
                check_path = Path(watch_path)
            else:
                check_path = base_path / watch_path.lstrip('/')

            if file_str.startswith(str(check_path)) or str(file_path).startswith(str(check_path)):
                return True
        return False

    def _schedule_review(self, file_path: Path):
        """Schedule a review for the file"""
        file_str = str(file_path)
        if file_str not in self.pending_reviews:
            self.pending_reviews.add(file_str)
            asyncio.create_task(self.review_service.review_file(file_path))
            # Remove from pending after 5 seconds to allow re-review
            asyncio.get_event_loop().call_later(5, self.pending_reviews.discard, file_str)


class CodeReviewService:
    """Main code review service"""

    def __init__(self):
        self.settings = Settings()
        self.session: aiohttp.ClientSession | None = None
        self.observer: Observer | None = None

    async def initialize(self):
        """Initialize the service"""
        self.session = aiohttp.ClientSession()
        logger.info("Initialized Code Review Service")
        logger.info(f"Ollama URL: {self.settings.ollama_url}")
        logger.info(f"Model: {self.settings.ollama_model}")
        logger.info(f"Watch paths: {self.settings.watch_paths}")
        logger.info(f"API Server: {self.settings.api_host}:{self.settings.api_port}")

    async def check_ollama_health(self) -> bool:
        """Check if Ollama service is available"""
        try:
            url = f"{self.settings.ollama_url}/api/tags"
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False

    async def close(self):
        """Close the service"""
        if self.session:
            await self.session.close()
        if self.observer:
            self.observer.stop()
            self.observer.join()

    async def review_file(self, file_path: Path):
        """Review a single file using Ollama"""
        try:
            # Read file content
            with open(file_path, encoding='utf-8', errors='ignore') as f:
                content = f.read()

            if not content.strip():
                return

            # Create review prompt
            prompt = self._create_review_prompt(file_path, content)

            # Get review from Ollama
            review = await self._get_ollama_review(prompt)

            # Log review
            self._log_review(file_path, review)

        except Exception as e:
            logger.error(f"Error reviewing {file_path}: {e}")

    async def review_code(self, code: str, language: str | None = None, filename: str | None = None) -> dict:
        """Review code content directly using Ollama"""
        try:
            if not code.strip():
                raise ValueError("Code content cannot be empty")

            # Create a pseudo file path for context
            if filename:
                file_path = Path(filename)
            elif language:
                file_path = Path(f"code.{language}")
            else:
                file_path = Path("code.txt")

            # Create review prompt
            prompt = self._create_review_prompt(file_path, code, language)

            # Get review from Ollama
            review = await self._get_ollama_review(prompt)

            if "error" in review:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Review failed: {review.get('error')}"
                )

            return review

        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error reviewing code: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred during review: {str(e)}"
            )

    def _create_review_prompt(self, file_path: Path, content: str, language: str | None = None) -> str:
        """Create a review prompt for Ollama"""
        file_ext = file_path.suffix

        # Determine file type
        if language:
            file_type = language.capitalize()
        else:
            file_type = {
                '.py': 'Python',
                '.ts': 'TypeScript',
                '.tsx': 'TypeScript React',
                '.js': 'JavaScript',
                '.jsx': 'JavaScript React',
                '.yml': 'YAML',
                '.yaml': 'YAML',
                '.json': 'JSON',
                '.md': 'Markdown',
                '.sh': 'Bash',
                '.dockerfile': 'Dockerfile',
                '.tf': 'Terraform',
                '.go': 'Go',
                '.rs': 'Rust'
            }.get(file_ext, 'Code')

        prompt = f"""You are an expert code reviewer. Review the following {file_type} file for:
1. Code quality and best practices
2. Security vulnerabilities
3. Performance issues
4. Docker/containerization best practices (if applicable)
5. Configuration errors
6. Potential bugs

File: {file_path}
Path: {file_path}

Code:
```{file_ext[1:] if file_ext else 'text'}
{content[:5000]}  # Limit to 5000 chars
```

Provide a concise review with:
- Summary (1-2 sentences)
- Critical issues (if any)
- Suggestions for improvement
- Security concerns (if any)

Format your response as JSON:
{{
  "summary": "...",
  "critical_issues": [...],
  "suggestions": [...],
  "security_concerns": [...],
  "score": 0-100
}}
"""
        return prompt

    async def _get_ollama_review(self, prompt: str) -> dict:
        """Get review from Ollama API"""
        try:
            url = f"{self.settings.ollama_url}/api/generate"
            payload = {
                "model": self.settings.ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "max_tokens": 2000
                }
            }

            async with self.session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=60)) as response:
                if response.status == 200:
                    data = await response.json()
                    response_text = data.get('response', '')

                    # Try to parse JSON from response
                    try:
                        # Extract JSON from markdown code blocks if present
                        if '```json' in response_text:
                            json_start = response_text.find('```json') + 7
                            json_end = response_text.find('```', json_start)
                            response_text = response_text[json_start:json_end].strip()
                        elif '```' in response_text:
                            json_start = response_text.find('```') + 3
                            json_end = response_text.find('```', json_start)
                            response_text = response_text[json_start:json_end].strip()

                        return json.loads(response_text)
                    except json.JSONDecodeError:
                        # Fallback to text response
                        return {
                            "summary": response_text[:500],
                            "critical_issues": [],
                            "suggestions": [],
                            "security_concerns": [],
                            "score": 75
                        }
                else:
                    logger.error(f"Ollama API error: {response.status}")
                    return {"error": f"API returned status {response.status}"}

        except TimeoutError:
            logger.error("Ollama API timeout")
            return {"error": "Request timeout"}
        except Exception as e:
            logger.error(f"Error calling Ollama API: {e}")
            return {"error": str(e)}

    def _log_review(self, file_path: Path, review: dict):
        """Log the review results"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "file": str(file_path),
            "review": review
        }

        # Log to file
        log_file = Path('/app/logs/reviews.jsonl')
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')

        # Log to console
        if "error" not in review:
            score = review.get('score', 'N/A')
            summary = review.get('summary', 'No summary')
            logger.info(f"📝 Review [{score}/100] {file_path.name}: {summary[:100]}")

            if review.get('critical_issues'):
                logger.warning(f"⚠️  Critical issues in {file_path.name}: {review['critical_issues']}")
            if review.get('security_concerns'):
                logger.error(f"🔒 Security concerns in {file_path.name}: {review['security_concerns']}")
        else:
            logger.error(f"❌ Review failed for {file_path.name}: {review.get('error')}")

    def start_watching(self):
        """Start watching the codebase"""
        event_handler = CodeReviewHandler(self)
        self.observer = Observer()

        # Watch multiple paths
        watch_paths = self.settings.watch_paths.split(':')
        base_path = Path('/app/codebase')

        for watch_path in watch_paths:
            watch_path = watch_path.strip()
            if not watch_path:
                continue
            # Handle both absolute and relative paths
            if watch_path.startswith('/'):
                full_path = Path(watch_path)
            else:
                full_path = base_path / watch_path.lstrip('/')

            if full_path.exists():
                self.observer.schedule(event_handler, str(full_path), recursive=True)
                logger.info(f"👀 Watching: {full_path}")
            else:
                logger.warning(f"⚠️  Path not found: {full_path}")

        self.observer.start()
        logger.info("🚀 Code review service started - monitoring for changes...")

        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping code review service...")
            self.observer.stop()
            self.observer.join()


# ═══════════════════════════════════════════════════════════════════════════
# FastAPI Application
# ═══════════════════════════════════════════════════════════════════════════

# Global service instance
_service_instance = None

def get_service() -> CodeReviewService:
    """Get or create the service instance"""
    global _service_instance
    if _service_instance is None:
        _service_instance = CodeReviewService()
    return _service_instance


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    # Startup
    service = get_service()
    await service.initialize()

    # Start file watcher in background if enabled
    if service.settings.review_on_change:
        import threading
        watch_thread = threading.Thread(target=service.start_watching, daemon=True)
        watch_thread.start()
        logger.info("File watcher started")

    yield

    # Shutdown
    await service.close()


# Create FastAPI app with lifespan
app = FastAPI(
    title="Code Review Service",
    description="Real-time code review service using Ollama + DeepSeek",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    service = get_service()
    ollama_ok = await service.check_ollama_health()
    return HealthResponse(
        status="healthy" if ollama_ok else "degraded",
        service="code-review-service",
        ollama_connected=ollama_ok
    )


@app.post("/review", response_model=ReviewResponse)
async def review_code_endpoint(request: CodeReviewRequest):
    """
    Review code content
    
    - **code**: Code content to review
    - **language**: Optional programming language hint
    - **filename**: Optional filename for context
    """
    service = get_service()
    review = await service.review_code(
        code=request.code,
        language=request.language,
        filename=request.filename
    )
    return ReviewResponse(**review)


@app.post("/review/file", response_model=ReviewResponse)
async def review_file_endpoint(request: FileReviewRequest):
    """
    Review a file from the codebase
    
    - **file_path**: Relative or absolute path to file in codebase
    """
    service = get_service()

    # Resolve file path
    base_path = Path('/app/codebase')
    file_path = Path(request.file_path)

    # Handle relative paths
    if not file_path.is_absolute():
        file_path = base_path / file_path

    # Verify file exists
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found: {request.file_path}"
        )

    # Verify file is within codebase
    try:
        file_path.relative_to(base_path)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="File must be within the codebase directory"
        )

    # Check file size
    if file_path.stat().st_size > service.settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {service.settings.max_file_size} bytes"
        )

    # Read and review file
    try:
        with open(file_path, encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read file: {str(e)}"
        )

    review = await service.review_code(
        code=content,
        filename=str(file_path.name)
    )
    return ReviewResponse(**review)


async def main():
    """Main entry point"""
    service = get_service()
    await service.initialize()

    try:
        # Start file watcher in background if enabled
        if service.settings.review_on_change:
            import threading
            watch_thread = threading.Thread(target=service.start_watching, daemon=True)
            watch_thread.start()
            logger.info("File watcher started")

        # Start API server
        config = uvicorn.Config(
            app,
            host=service.settings.api_host,
            port=service.settings.api_port,
            log_level=service.settings.log_level.lower()
        )
        server = uvicorn.Server(config)
        await server.serve()

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        await service.close()


if __name__ == "__main__":
    asyncio.run(main())


