"""
Virus Scanner Interfaces and Implementations
واجهات وتطبيقات فاحص الفيروسات
"""

import asyncio
import hashlib
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

import httpx

logger = logging.getLogger(__name__)


class ScanVerdict(Enum):
    """Virus scan verdict"""

    CLEAN = "clean"
    MALICIOUS = "malicious"
    SUSPICIOUS = "suspicious"
    UNKNOWN = "unknown"
    ERROR = "error"


@dataclass
class ScanResult:
    """Result of a virus scan"""

    verdict: ScanVerdict
    malicious_count: int = 0
    suspicious_count: int = 0
    total_engines: int = 0
    scan_id: str | None = None
    details: dict | None = None


class VirusScannerInterface(ABC):
    """
    Abstract interface for virus scanners
    واجهة مجردة لفاحصي الفيروسات
    """

    @abstractmethod
    async def scan(self, file_content: bytes, filename: str) -> bool:
        """
        Scan file content for viruses
        فحص محتوى الملف بحثاً عن فيروسات

        Args:
            file_content: File content as bytes
            filename: Filename for logging

        Returns:
            True if file is safe, False if virus detected
        """
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """
        Check if scanner is available
        التحقق من توفر الفاحص

        Returns:
            True if scanner is available
        """
        pass


class NoOpScanner(VirusScannerInterface):
    """
    No-operation scanner (does not perform actual scanning)
    فاحص غير فعال (لا يقوم بالفحص الفعلي)

    Use this as a placeholder when virus scanning is not enabled
    """

    async def scan(self, file_content: bytes, filename: str) -> bool:
        """Always returns True (no scanning performed)"""
        return True

    async def is_available(self) -> bool:
        """Always returns False (not a real scanner)"""
        return False


class ClamAVScanner(VirusScannerInterface):
    """
    ClamAV virus scanner implementation
    تطبيق فاحص الفيروسات ClamAV

    Requires ClamAV daemon (clamd) to be running
    يتطلب تشغيل خدمة ClamAV (clamd)
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 3310,
        timeout: int = 30,
    ):
        """
        Initialize ClamAV scanner

        Args:
            host: ClamAV daemon host
            port: ClamAV daemon port
            timeout: Scan timeout in seconds
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self._available: bool | None = None

    async def scan(self, file_content: bytes, filename: str) -> bool:
        """
        Scan file using ClamAV
        فحص الملف باستخدام ClamAV

        Args:
            file_content: File content as bytes
            filename: Filename for logging

        Returns:
            True if file is safe, False if virus detected
        """
        try:
            # Check if scanner is available
            if not await self.is_available():
                logger.warning("ClamAV not available, skipping scan")
                return True

            # Send INSTREAM command to ClamAV
            reader, writer = await asyncio.wait_for(asyncio.open_connection(self.host, self.port), timeout=self.timeout)

            try:
                # Send INSTREAM command
                writer.write(b"zINSTREAM\0")
                await writer.drain()

                # Send file content in chunks
                chunk_size = 2048
                for i in range(0, len(file_content), chunk_size):
                    chunk = file_content[i : i + chunk_size]
                    # Send chunk size (4 bytes, big-endian)
                    size_bytes = len(chunk).to_bytes(4, byteorder="big")
                    writer.write(size_bytes)
                    writer.write(chunk)
                    await writer.drain()

                # Send zero-length chunk to signal end
                writer.write(b"\x00\x00\x00\x00")
                await writer.drain()

                # Read response
                response = await asyncio.wait_for(reader.read(1024), timeout=self.timeout)
                response_str = response.decode("utf-8").strip()

                # Check response
                if "OK" in response_str:
                    logger.info(f"File {filename} scanned: clean")
                    return True
                else:
                    logger.warning(f"Virus detected in {filename}: {response_str}")
                    return False

            finally:
                writer.close()
                await writer.wait_closed()

        except TimeoutError:
            logger.error(f"ClamAV scan timeout for {filename}")
            # In case of timeout, we might want to allow or reject
            # For security, we'll reject
            return False

        except Exception as e:
            logger.error(f"Error scanning {filename} with ClamAV: {e}")
            # In case of error, we might want to allow or reject
            # For security, we'll reject
            return False

    async def is_available(self) -> bool:
        """
        Check if ClamAV is available
        التحقق من توفر ClamAV

        Returns:
            True if ClamAV is available
        """
        if self._available is not None:
            return self._available

        try:
            # Try to connect and send PING command
            reader, writer = await asyncio.wait_for(asyncio.open_connection(self.host, self.port), timeout=5)

            try:
                writer.write(b"zPING\0")
                await writer.drain()

                response = await asyncio.wait_for(reader.read(1024), timeout=5)
                response_str = response.decode("utf-8").strip()

                self._available = "PONG" in response_str
                return self._available

            finally:
                writer.close()
                await writer.wait_closed()

        except Exception as e:
            logger.warning(f"ClamAV not available: {e}")
            self._available = False
            return False


class VirusTotalScanner(VirusScannerInterface):
    """
    VirusTotal cloud-based virus scanner implementation
    تطبيق فاحص الفيروسات السحابي VirusTotal

    Integrates with VirusTotal API v3 for file scanning
    """

    BASE_URL = "https://www.virustotal.com/api/v3"
    # VirusTotal free tier: 4 requests/minute, 500 requests/day
    DEFAULT_RATE_LIMIT_DELAY = 15.0  # seconds between requests
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_RETRY_DELAY = 5.0  # seconds
    DEFAULT_POLL_INTERVAL = 10.0  # seconds
    DEFAULT_POLL_TIMEOUT = 300.0  # 5 minutes max wait for analysis
    # Threshold for malicious/suspicious detections to consider file unsafe
    DEFAULT_MALICIOUS_THRESHOLD = 1
    DEFAULT_SUSPICIOUS_THRESHOLD = 3

    def __init__(
        self,
        api_key: str | None = None,
        timeout: int = 60,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_delay: float = DEFAULT_RETRY_DELAY,
        rate_limit_delay: float = DEFAULT_RATE_LIMIT_DELAY,
        poll_interval: float = DEFAULT_POLL_INTERVAL,
        poll_timeout: float = DEFAULT_POLL_TIMEOUT,
        malicious_threshold: int = DEFAULT_MALICIOUS_THRESHOLD,
        suspicious_threshold: int = DEFAULT_SUSPICIOUS_THRESHOLD,
    ):
        """
        Initialize VirusTotal scanner

        Args:
            api_key: VirusTotal API key
            timeout: HTTP request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            rate_limit_delay: Delay between requests for rate limiting
            poll_interval: Interval between polling for analysis results
            poll_timeout: Maximum time to wait for analysis completion
            malicious_threshold: Number of malicious detections to mark as unsafe
            suspicious_threshold: Number of suspicious detections to mark as unsafe
        """
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.rate_limit_delay = rate_limit_delay
        self.poll_interval = poll_interval
        self.poll_timeout = poll_timeout
        self.malicious_threshold = malicious_threshold
        self.suspicious_threshold = suspicious_threshold
        self._last_request_time: float = 0
        self._rate_limit_lock = asyncio.Lock()

    def _get_headers(self) -> dict[str, str]:
        """Get HTTP headers with API key"""
        return {
            "x-apikey": self.api_key or "",
            "Accept": "application/json",
        }

    @staticmethod
    def _compute_sha256(file_content: bytes) -> str:
        """Compute SHA256 hash of file content"""
        return hashlib.sha256(file_content).hexdigest()

    async def _wait_for_rate_limit(self) -> None:
        """Wait if needed to respect rate limits"""
        async with self._rate_limit_lock:
            import time

            current_time = time.time()
            elapsed = current_time - self._last_request_time
            if elapsed < self.rate_limit_delay:
                wait_time = self.rate_limit_delay - elapsed
                logger.debug(f"Rate limiting: waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)
            self._last_request_time = time.time()

    async def _make_request(
        self,
        client: httpx.AsyncClient,
        method: str,
        url: str,
        **kwargs,
    ) -> httpx.Response:
        """
        Make HTTP request with retries and rate limiting

        Args:
            client: HTTP client
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            **kwargs: Additional request arguments

        Returns:
            HTTP response

        Raises:
            httpx.HTTPError: If request fails after all retries
        """
        last_exception: Exception | None = None

        for attempt in range(self.max_retries):
            try:
                await self._wait_for_rate_limit()

                response = await client.request(method, url, **kwargs)

                # Handle rate limiting (HTTP 429)
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", self.retry_delay * 2))
                    logger.warning(f"Rate limited by VirusTotal, waiting {retry_after}s")
                    await asyncio.sleep(retry_after)
                    continue

                # Raise for other HTTP errors
                response.raise_for_status()
                return response

            except httpx.HTTPStatusError as e:
                last_exception = e
                if e.response.status_code == 429:
                    # Already handled above, but just in case
                    continue
                elif e.response.status_code >= 500:
                    # Server error, retry
                    logger.warning(f"VirusTotal server error (attempt {attempt + 1}): {e}")
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                else:
                    # Client error, don't retry
                    raise

            except (httpx.ConnectError, httpx.TimeoutException) as e:
                last_exception = e
                logger.warning(f"VirusTotal connection error (attempt {attempt + 1}): {e}")
                await asyncio.sleep(self.retry_delay * (attempt + 1))
                continue

        raise last_exception or Exception("Request failed after all retries")

    async def _check_existing_report(
        self,
        client: httpx.AsyncClient,
        file_hash: str,
    ) -> ScanResult | None:
        """
        Check if file has already been scanned by hash

        Args:
            client: HTTP client
            file_hash: SHA256 hash of file

        Returns:
            ScanResult if report exists, None otherwise
        """
        try:
            url = f"{self.BASE_URL}/files/{file_hash}"
            response = await self._make_request(client, "GET", url, headers=self._get_headers())
            return self._parse_analysis_response(response.json())

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                # File not found in VirusTotal database
                return None
            raise

    async def _upload_file(
        self,
        client: httpx.AsyncClient,
        file_content: bytes,
        filename: str,
    ) -> str:
        """
        Upload file to VirusTotal for scanning

        Args:
            client: HTTP client
            file_content: File content as bytes
            filename: Original filename

        Returns:
            Analysis ID for polling
        """
        # For files > 32MB, need to get upload URL first
        if len(file_content) > 32 * 1024 * 1024:
            url_response = await self._make_request(
                client, "GET", f"{self.BASE_URL}/files/upload_url", headers=self._get_headers()
            )
            upload_url = url_response.json()["data"]
        else:
            upload_url = f"{self.BASE_URL}/files"

        files = {"file": (filename, file_content)}
        response = await self._make_request(
            client,
            "POST",
            upload_url,
            headers=self._get_headers(),
            files=files,
            timeout=max(self.timeout, 120),  # Allow more time for upload
        )

        data = response.json()
        analysis_id = data["data"]["id"]
        logger.info(f"File {filename} uploaded to VirusTotal, analysis ID: {analysis_id}")
        return analysis_id

    async def _poll_analysis(
        self,
        client: httpx.AsyncClient,
        analysis_id: str,
    ) -> ScanResult:
        """
        Poll for analysis completion

        Args:
            client: HTTP client
            analysis_id: Analysis ID from upload

        Returns:
            ScanResult with analysis results
        """
        url = f"{self.BASE_URL}/analyses/{analysis_id}"
        start_time = asyncio.get_event_loop().time()

        while True:
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > self.poll_timeout:
                logger.error(f"Analysis timeout after {elapsed:.0f}s")
                return ScanResult(verdict=ScanVerdict.ERROR, details={"error": "Analysis timeout"})

            response = await self._make_request(client, "GET", url, headers=self._get_headers())
            data = response.json()

            status = data["data"]["attributes"]["status"]
            if status == "completed":
                return self._parse_analysis_response(data)
            elif status in ("queued", "in-progress"):
                logger.debug(f"Analysis in progress, waiting {self.poll_interval}s...")
                await asyncio.sleep(self.poll_interval)
            else:
                logger.error(f"Unknown analysis status: {status}")
                return ScanResult(verdict=ScanVerdict.ERROR, details={"error": f"Unknown status: {status}"})

    def _parse_analysis_response(self, response_data: dict) -> ScanResult:
        """
        Parse VirusTotal analysis response into ScanResult

        Args:
            response_data: Raw API response

        Returns:
            Parsed ScanResult
        """
        try:
            attributes = response_data.get("data", {}).get("attributes", {})

            # Handle both file report and analysis response formats
            if "last_analysis_stats" in attributes:
                stats = attributes["last_analysis_stats"]
            elif "stats" in attributes:
                stats = attributes["stats"]
            else:
                return ScanResult(
                    verdict=ScanVerdict.UNKNOWN,
                    details={"error": "No analysis stats found"},
                )

            malicious = stats.get("malicious", 0)
            suspicious = stats.get("suspicious", 0)
            total = sum(stats.values())

            # Determine verdict based on thresholds
            if malicious >= self.malicious_threshold:
                verdict = ScanVerdict.MALICIOUS
            elif suspicious >= self.suspicious_threshold:
                verdict = ScanVerdict.SUSPICIOUS
            elif malicious == 0 and suspicious == 0:
                verdict = ScanVerdict.CLEAN
            else:
                verdict = ScanVerdict.CLEAN  # Below thresholds

            scan_id = response_data.get("data", {}).get("id")

            return ScanResult(
                verdict=verdict,
                malicious_count=malicious,
                suspicious_count=suspicious,
                total_engines=total,
                scan_id=scan_id,
                details=stats,
            )

        except Exception as e:
            logger.error(f"Error parsing VirusTotal response: {e}")
            return ScanResult(verdict=ScanVerdict.ERROR, details={"error": str(e)})

    async def scan_with_result(self, file_content: bytes, filename: str) -> ScanResult:
        """
        Scan file and return detailed result

        Args:
            file_content: File content as bytes
            filename: Filename for logging

        Returns:
            ScanResult with detailed scan information
        """
        if not self.api_key:
            logger.warning("VirusTotal API key not configured")
            return ScanResult(verdict=ScanVerdict.ERROR, details={"error": "API key not configured"})

        file_hash = self._compute_sha256(file_content)
        logger.info(f"Scanning file {filename} (SHA256: {file_hash})")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # First, check if file has already been analyzed
                existing_result = await self._check_existing_report(client, file_hash)
                if existing_result:
                    logger.info(
                        f"Found existing VirusTotal report for {filename}: "
                        f"{existing_result.verdict.value} "
                        f"({existing_result.malicious_count} malicious, "
                        f"{existing_result.suspicious_count} suspicious)"
                    )
                    return existing_result

                # Upload file for new analysis
                analysis_id = await self._upload_file(client, file_content, filename)

                # Poll for results
                result = await self._poll_analysis(client, analysis_id)
                logger.info(
                    f"VirusTotal scan complete for {filename}: "
                    f"{result.verdict.value} "
                    f"({result.malicious_count} malicious, "
                    f"{result.suspicious_count} suspicious)"
                )
                return result

        except httpx.HTTPStatusError as e:
            logger.error(f"VirusTotal API error for {filename}: {e}")
            return ScanResult(
                verdict=ScanVerdict.ERROR,
                details={"error": f"HTTP {e.response.status_code}: {e.response.text}"},
            )
        except Exception as e:
            logger.error(f"Error scanning {filename} with VirusTotal: {e}")
            return ScanResult(verdict=ScanVerdict.ERROR, details={"error": str(e)})

    async def scan(self, file_content: bytes, filename: str) -> bool:
        """
        Scan file content for viruses using VirusTotal API
        فحص محتوى الملف بحثاً عن فيروسات باستخدام VirusTotal

        Args:
            file_content: File content as bytes
            filename: Filename for logging

        Returns:
            True if file is safe, False if virus detected or scan error
        """
        result = await self.scan_with_result(file_content, filename)

        # Consider file unsafe if malicious, suspicious, or error
        if result.verdict in (ScanVerdict.MALICIOUS, ScanVerdict.SUSPICIOUS):
            return False
        elif result.verdict == ScanVerdict.ERROR:
            # For security, reject files that couldn't be scanned
            logger.warning(f"Scan error for {filename}, rejecting for safety")
            return False

        return True

    async def is_available(self) -> bool:
        """
        Check if VirusTotal scanner is configured and accessible
        التحقق من توفر فاحص VirusTotal

        Returns:
            True if scanner is available
        """
        if not self.api_key:
            return False

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                # Test API key by checking quota
                response = await client.get(
                    f"{self.BASE_URL}/users/current",
                    headers=self._get_headers(),
                )
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"VirusTotal not available: {e}")
            return False


# Alias for backward compatibility
CloudVirusScannerStub = VirusTotalScanner


def get_virus_scanner(scanner_type: str = "noop", **kwargs) -> VirusScannerInterface:
    """
    Factory function to get virus scanner instance
    وظيفة مصنعية للحصول على نسخة من فاحص الفيروسات

    Args:
        scanner_type: Type of scanner ("noop", "clamav", "cloud", "virustotal")
        **kwargs: Additional arguments for scanner initialization

    Returns:
        VirusScannerInterface instance
    """
    if scanner_type == "clamav":
        return ClamAVScanner(**kwargs)
    elif scanner_type in ("cloud", "virustotal"):
        return VirusTotalScanner(**kwargs)
    else:
        return NoOpScanner()
