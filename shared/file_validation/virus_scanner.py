"""
Virus Scanner Interfaces and Implementations
واجهات وتطبيقات فاحص الفيروسات
"""

from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


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


class CloudVirusScanner(VirusScannerInterface):
    """
    Cloud-based virus scanner using VirusTotal API
    فاحص الفيروسات السحابي باستخدام VirusTotal API

    Supports VirusTotal API for comprehensive malware scanning
    يدعم واجهة VirusTotal للفحص الشامل عن البرمجيات الخبيثة
    """

    VIRUSTOTAL_API_URL = "https://www.virustotal.com/api/v3"

    def __init__(
        self,
        api_key: str | None = None,
        timeout: int = 60,
        detection_threshold: int = 3,
    ):
        """
        Initialize cloud scanner with VirusTotal API

        Args:
            api_key: VirusTotal API key (from environment or parameter)
            timeout: Request timeout in seconds
            detection_threshold: Number of positive detections to consider file malicious
        """
        import os

        self.api_key = api_key or os.getenv("VIRUSTOTAL_API_KEY")
        self.timeout = timeout
        self.detection_threshold = detection_threshold
        self._http_client = None

    async def _get_client(self):
        """Get or create HTTP client lazily"""
        if self._http_client is None:
            import httpx

            self._http_client = httpx.AsyncClient(
                timeout=self.timeout,
                headers={
                    "x-apikey": self.api_key or "",
                    "Accept": "application/json",
                },
            )
        return self._http_client

    async def scan(self, file_content: bytes, filename: str) -> bool:
        """
        Scan file using VirusTotal API
        فحص الملف باستخدام واجهة VirusTotal

        Args:
            file_content: File content as bytes
            filename: Filename for logging and upload

        Returns:
            True if file is safe, False if malware detected
        """
        if not self.api_key:
            logger.warning("VirusTotal API key not configured, skipping scan for %s", filename)  # nosemgrep: python-logger-credential-disclosure -- logs filename, not credentials
            return True

        try:
            import hashlib

            # Calculate file hash first (to check if already analyzed)
            file_hash = hashlib.sha256(file_content).hexdigest()
            logger.info("Checking VirusTotal for file %s (SHA256: %s)", filename, file_hash[:16])

            client = await self._get_client()

            # First, check if file was already analyzed
            existing_result = await self._check_existing_report(client, file_hash)
            if existing_result is not None:
                return existing_result

            # If not found, upload and scan
            return await self._upload_and_scan(client, file_content, filename)

        except Exception as e:
            logger.error("Cloud scan error for %s: %s", filename, str(e))
            # Fail-open: allow file if scanning fails (configurable in production)
            return True

    async def _check_existing_report(self, client, file_hash: str) -> bool | None:
        """
        Check if file already has a VirusTotal report
        التحقق من وجود تقرير سابق للملف

        Returns:
            True if safe, False if malicious, None if not found
        """
        try:
            response = await client.get(f"{self.VIRUSTOTAL_API_URL}/files/{file_hash}")

            if response.status_code == 200:
                data = response.json()
                stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
                malicious = stats.get("malicious", 0)
                suspicious = stats.get("suspicious", 0)

                total_detections = malicious + suspicious
                is_safe = total_detections < self.detection_threshold

                logger.info(
                    "VirusTotal report found: malicious=%d, suspicious=%d, threshold=%d, safe=%s",
                    malicious,
                    suspicious,
                    self.detection_threshold,
                    is_safe,
                )
                return is_safe

            elif response.status_code == 404:
                logger.info("No existing VirusTotal report found")
                return None

        except Exception as e:
            logger.warning("Error checking existing report: %s", str(e))

        return None

    async def _upload_and_scan(self, client, file_content: bytes, filename: str) -> bool:
        """
        Upload file to VirusTotal for scanning
        رفع الملف إلى VirusTotal للفحص

        Returns:
            True if safe, False if malicious
        """
        try:
            # Upload file for scanning
            files = {"file": (filename, file_content)}
            response = await client.post(
                f"{self.VIRUSTOTAL_API_URL}/files",
                files=files,
            )

            if response.status_code not in (200, 201):
                logger.warning("VirusTotal upload failed: %s", response.status_code)
                return True  # Fail-open

            data = response.json()
            analysis_id = data.get("data", {}).get("id")

            if not analysis_id:
                logger.warning("No analysis ID returned from VirusTotal")
                return True

            logger.info("File uploaded to VirusTotal, analysis ID: %s", analysis_id[:16])

            # Poll for results (with timeout)
            return await self._poll_analysis_result(client, analysis_id)

        except Exception as e:
            logger.error("Error uploading to VirusTotal: %s", str(e))
            return True  # Fail-open

    async def _poll_analysis_result(
        self,
        client,
        analysis_id: str,
        max_attempts: int = 10,
        poll_interval: int = 5,
    ) -> bool:
        """
        Poll VirusTotal for analysis results
        انتظار نتائج الفحص من VirusTotal
        """
        for attempt in range(max_attempts):
            try:
                response = await client.get(f"{self.VIRUSTOTAL_API_URL}/analyses/{analysis_id}")

                if response.status_code == 200:
                    data = response.json()
                    status = data.get("data", {}).get("attributes", {}).get("status")

                    if status == "completed":
                        stats = data.get("data", {}).get("attributes", {}).get("stats", {})
                        malicious = stats.get("malicious", 0)
                        suspicious = stats.get("suspicious", 0)

                        total_detections = malicious + suspicious
                        is_safe = total_detections < self.detection_threshold

                        logger.info(
                            "VirusTotal scan complete: malicious=%d, suspicious=%d, safe=%s",
                            malicious,
                            suspicious,
                            is_safe,
                        )
                        return is_safe

                    elif status in ("queued", "in-progress"):
                        logger.debug("Analysis in progress, attempt %d/%d", attempt + 1, max_attempts)
                        await asyncio.sleep(poll_interval)
                        continue

            except Exception as e:
                logger.warning("Error polling analysis: %s", str(e))

            await asyncio.sleep(poll_interval)

        logger.warning("Analysis polling timeout, assuming safe")
        return True  # Fail-open on timeout

    async def is_available(self) -> bool:
        """Check if cloud scanner is configured and reachable"""
        if not self.api_key:
            return False

        try:
            client = await self._get_client()
            # Test API connectivity
            response = await client.get(f"{self.VIRUSTOTAL_API_URL}/users/current")
            return response.status_code == 200
        except Exception:
            return False

    async def close(self):
        """Close HTTP client"""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None


# Backward compatibility alias
CloudVirusScannerStub = CloudVirusScanner


def get_virus_scanner(scanner_type: str = "noop", **kwargs) -> VirusScannerInterface:
    """
    Factory function to get virus scanner instance
    وظيفة مصنعية للحصول على نسخة من فاحص الفيروسات

    Args:
        scanner_type: Type of scanner ("noop", "clamav", "cloud")
        **kwargs: Additional arguments for scanner initialization

    Returns:
        VirusScannerInterface instance
    """
    if scanner_type == "clamav":
        return ClamAVScanner(**kwargs)
    elif scanner_type == "cloud":
        return CloudVirusScannerStub(**kwargs)
    else:
        return NoOpScanner()
