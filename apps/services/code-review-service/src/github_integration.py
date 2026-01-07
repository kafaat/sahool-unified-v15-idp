"""
GitHub Integration Module
وحدة تكامل GitHub

Provides GitHub PR integration for automated code reviews
توفر تكامل PR في GitHub للمراجعات الآلية
"""

import hashlib
import hmac
import logging
from typing import Any, Optional

import aiohttp

logger = logging.getLogger(__name__)


class GitHubIntegration:
    """GitHub API integration for PR reviews"""

    def __init__(
        self,
        token: str,
        api_url: str = "https://api.github.com",
        webhook_secret: Optional[str] = None
    ):
        self.token = token
        self.api_url = api_url.rstrip("/")
        self.webhook_secret = webhook_secret
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self.session is None or self.session.closed:
            headers = {
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "SAHOOL-Code-Review-Service"
            }
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session

    async def close(self):
        """Close the HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify GitHub webhook signature"""
        if not self.webhook_secret:
            return True  # No secret configured, skip verification

        if not signature or not signature.startswith("sha256="):
            return False

        expected = "sha256=" + hmac.new(
            self.webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected)

    async def get_pr(self, owner: str, repo: str, pr_number: int) -> Optional[dict]:
        """Get PR details"""
        try:
            session = await self._get_session()
            url = f"{self.api_url}/repos/{owner}/{repo}/pulls/{pr_number}"
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                logger.error(f"Failed to get PR: {response.status}")
                return None
        except Exception as e:
            logger.error(f"Error getting PR: {e}")
            return None

    async def get_pr_files(self, owner: str, repo: str, pr_number: int) -> list[dict]:
        """Get list of files changed in a PR"""
        try:
            session = await self._get_session()
            url = f"{self.api_url}/repos/{owner}/{repo}/pulls/{pr_number}/files"
            files = []
            page = 1

            while True:
                async with session.get(url, params={"page": page, "per_page": 100}) as response:
                    if response.status != 200:
                        logger.error(f"Failed to get PR files: {response.status}")
                        break
                    page_files = await response.json()
                    if not page_files:
                        break
                    files.extend(page_files)
                    page += 1

            return files
        except Exception as e:
            logger.error(f"Error getting PR files: {e}")
            return []

    async def get_file_content(self, owner: str, repo: str, path: str, ref: str) -> Optional[str]:
        """Get file content from repository"""
        try:
            session = await self._get_session()
            url = f"{self.api_url}/repos/{owner}/{repo}/contents/{path}"
            async with session.get(url, params={"ref": ref}) as response:
                if response.status != 200:
                    return None
                data = await response.json()
                if data.get("encoding") == "base64":
                    import base64
                    return base64.b64decode(data["content"]).decode("utf-8")
                return data.get("content")
        except Exception as e:
            logger.error(f"Error getting file content: {e}")
            return None

    async def create_pr_comment(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        body: str
    ) -> Optional[dict]:
        """Create a comment on a PR"""
        try:
            session = await self._get_session()
            url = f"{self.api_url}/repos/{owner}/{repo}/issues/{pr_number}/comments"
            async with session.post(url, json={"body": body}) as response:
                if response.status == 201:
                    return await response.json()
                logger.error(f"Failed to create comment: {response.status}")
                return None
        except Exception as e:
            logger.error(f"Error creating comment: {e}")
            return None

    async def create_review(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        body: str,
        event: str = "COMMENT",  # APPROVE, REQUEST_CHANGES, COMMENT
        comments: Optional[list[dict]] = None
    ) -> Optional[dict]:
        """Create a PR review with inline comments"""
        try:
            session = await self._get_session()
            url = f"{self.api_url}/repos/{owner}/{repo}/pulls/{pr_number}/reviews"

            payload = {
                "body": body,
                "event": event
            }

            if comments:
                payload["comments"] = comments

            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                logger.error(f"Failed to create review: {response.status} - {error_text}")
                return None
        except Exception as e:
            logger.error(f"Error creating review: {e}")
            return None

    async def create_check_run(
        self,
        owner: str,
        repo: str,
        head_sha: str,
        name: str = "SAHOOL Code Review",
        status: str = "completed",
        conclusion: str = "neutral",  # success, failure, neutral, cancelled
        title: str = "Code Review Results",
        summary: str = "",
        annotations: Optional[list[dict]] = None
    ) -> Optional[dict]:
        """Create a check run (requires GitHub App)"""
        try:
            session = await self._get_session()
            url = f"{self.api_url}/repos/{owner}/{repo}/check-runs"

            payload = {
                "name": name,
                "head_sha": head_sha,
                "status": status,
                "conclusion": conclusion,
                "output": {
                    "title": title,
                    "summary": summary
                }
            }

            if annotations:
                payload["output"]["annotations"] = annotations[:50]  # GitHub limit

            async with session.post(url, json=payload) as response:
                if response.status == 201:
                    return await response.json()
                logger.error(f"Failed to create check run: {response.status}")
                return None
        except Exception as e:
            logger.error(f"Error creating check run: {e}")
            return None

    def format_review_comment(self, review: dict, file_path: str = None) -> str:
        """Format review results as GitHub markdown comment"""
        score = review.get("score", 0)
        summary = review.get("summary", "No summary available")
        critical = review.get("critical_issues", [])
        suggestions = review.get("suggestions", [])
        security = review.get("security_concerns", [])
        agricultural = review.get("agricultural_issues", [])

        # Score emoji
        if score >= 80:
            score_emoji = "✅"
            status = "جيد / Good"
        elif score >= 60:
            score_emoji = "⚠️"
            status = "يحتاج تحسين / Needs Improvement"
        else:
            score_emoji = "❌"
            status = "يحتاج مراجعة / Needs Review"

        lines = [
            "## 🔍 SAHOOL Code Review / مراجعة كود سهول",
            "",
            f"**Score / النتيجة:** {score_emoji} **{score}/100** ({status})",
            "",
        ]

        if file_path:
            lines.append(f"**File / الملف:** `{file_path}`")
            lines.append("")

        lines.extend([
            "### 📋 Summary / الملخص",
            summary,
            ""
        ])

        if critical:
            lines.append("### ❌ Critical Issues / مشاكل حرجة")
            for issue in critical:
                lines.append(f"- {issue}")
            lines.append("")

        if security:
            lines.append("### 🔒 Security Concerns / مخاوف أمنية")
            for concern in security:
                lines.append(f"- {concern}")
            lines.append("")

        if agricultural:
            lines.append("### 🌾 Agricultural Issues / مشاكل زراعية")
            for issue in agricultural:
                lines.append(f"- {issue}")
            lines.append("")

        if suggestions:
            lines.append("### 💡 Suggestions / اقتراحات")
            for suggestion in suggestions[:5]:  # Limit to 5
                lines.append(f"- {suggestion}")
            lines.append("")

        lines.extend([
            "---",
            "*Automated review by SAHOOL Code Review Service*",
            "*مراجعة آلية بواسطة خدمة مراجعة كود سهول*"
        ])

        return "\n".join(lines)

    def format_pr_summary(self, file_reviews: list[dict]) -> str:
        """Format multiple file reviews into a PR summary"""
        if not file_reviews:
            return "No files were reviewed."

        total_score = sum(r.get("score", 0) for r in file_reviews) // len(file_reviews)

        # Overall status
        if total_score >= 80:
            overall_emoji = "✅"
            overall_status = "Approved / موافق"
        elif total_score >= 60:
            overall_emoji = "⚠️"
            overall_status = "Needs Minor Changes / يحتاج تغييرات طفيفة"
        else:
            overall_emoji = "❌"
            overall_status = "Needs Review / يحتاج مراجعة"

        lines = [
            "# 🔍 SAHOOL Pull Request Review / مراجعة طلب السحب",
            "",
            f"## Overall Score / النتيجة الإجمالية: {overall_emoji} **{total_score}/100**",
            f"**Status / الحالة:** {overall_status}",
            "",
            f"**Files Reviewed / الملفات المراجعة:** {len(file_reviews)}",
            "",
            "## File Summaries / ملخص الملفات",
            "",
            "| File | Score | Status |",
            "|------|-------|--------|"
        ]

        # Sort by score (lowest first to highlight issues)
        sorted_reviews = sorted(file_reviews, key=lambda x: x.get("score", 0))

        for review in sorted_reviews:
            file_name = review.get("file", "Unknown")
            score = review.get("score", 0)
            emoji = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
            lines.append(f"| `{file_name}` | {emoji} {score} | {review.get('summary', 'N/A')[:50]}... |")

        # Aggregate issues
        all_critical = []
        all_security = []
        all_agricultural = []

        for review in file_reviews:
            file_name = review.get("file", "Unknown")
            for issue in review.get("critical_issues", []):
                all_critical.append(f"[{file_name}] {issue}")
            for concern in review.get("security_concerns", []):
                all_security.append(f"[{file_name}] {concern}")
            for issue in review.get("agricultural_issues", []):
                all_agricultural.append(f"[{file_name}] {issue}")

        lines.append("")

        if all_critical:
            lines.append("## ❌ Critical Issues / مشاكل حرجة")
            for issue in all_critical[:10]:
                lines.append(f"- {issue}")
            lines.append("")

        if all_security:
            lines.append("## 🔒 Security Concerns / مخاوف أمنية")
            for concern in all_security[:10]:
                lines.append(f"- {concern}")
            lines.append("")

        if all_agricultural:
            lines.append("## 🌾 Agricultural Issues / مشاكل زراعية")
            for issue in all_agricultural[:10]:
                lines.append(f"- {issue}")
            lines.append("")

        lines.extend([
            "---",
            "*Automated review by SAHOOL Code Review Service v2.0*",
            "*مراجعة آلية بواسطة خدمة مراجعة كود سهول الإصدار 2.0*"
        ])

        return "\n".join(lines)


class PRReviewResult:
    """Container for PR review results"""

    def __init__(self, pr_number: int, owner: str, repo: str):
        self.pr_number = pr_number
        self.owner = owner
        self.repo = repo
        self.file_reviews: list[dict] = []
        self.total_score: int = 0
        self.files_reviewed: int = 0

    def add_file_review(self, file_path: str, review: dict):
        """Add a file review result"""
        review["file"] = file_path
        self.file_reviews.append(review)
        self.files_reviewed += 1
        self._update_score()

    def _update_score(self):
        """Update total score"""
        if self.file_reviews:
            self.total_score = sum(r.get("score", 0) for r in self.file_reviews) // len(self.file_reviews)

    def get_conclusion(self) -> str:
        """Get GitHub check run conclusion"""
        if self.total_score >= 80:
            return "success"
        elif self.total_score >= 60:
            return "neutral"
        else:
            return "failure"

    def has_critical_issues(self) -> bool:
        """Check if any file has critical issues"""
        return any(r.get("critical_issues") for r in self.file_reviews)

    def has_security_concerns(self) -> bool:
        """Check if any file has security concerns"""
        return any(r.get("security_concerns") for r in self.file_reviews)
