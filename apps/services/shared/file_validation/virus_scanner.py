"""
Virus Scanner Interfaces and Implementations
واجهات وتطبيقات فاحص الفيروسات
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Optional

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
        self._available: Optional[bool] = None

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
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=self.timeout
            )

            try:
                # Send INSTREAM command
                writer.write(b"zINSTREAM\0")
                await writer.drain()

                # Send file content in chunks
                chunk_size = 2048
                for i in range(0, len(file_content), chunk_size):
                    chunk = file_content[i:i + chunk_size]
                    # Send chunk size (4 bytes, big-endian)
                    size_bytes = len(chunk).to_bytes(4, byteorder='big')
                    writer.write(size_bytes)
                    writer.write(chunk)
                    await writer.drain()

                # Send zero-length chunk to signal end
                writer.write(b'\x00\x00\x00\x00')
                await writer.drain()

                # Read response
                response = await asyncio.wait_for(
                    reader.read(1024),
                    timeout=self.timeout
                )
                response_str = response.decode('utf-8').strip()

                # Check response
                if 'OK' in response_str:
                    logger.info(f"File {filename} scanned: clean")
                    return True
                else:
                    logger.warning(f"Virus detected in {filename}: {response_str}")
                    return False

            finally:
                writer.close()
                await writer.wait_closed()

        except asyncio.TimeoutError:
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
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=5
            )

            try:
                writer.write(b"zPING\0")
                await writer.drain()

                response = await asyncio.wait_for(reader.read(1024), timeout=5)
                response_str = response.decode('utf-8').strip()

                self._available = 'PONG' in response_str
                return self._available

            finally:
                writer.close()
                await writer.wait_closed()

        except Exception as e:
            logger.warning(f"ClamAV not available: {e}")
            self._available = False
            return False


class CloudVirusScannerStub(VirusScannerInterface):
    """
    Stub for cloud-based virus scanner (e.g., VirusTotal, AWS S3 Malware Scanning)
    بديل لفاحص الفيروسات السحابي

    This is a placeholder for integration with cloud scanning services
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize cloud scanner stub

        Args:
            api_key: API key for cloud service
        """
        self.api_key = api_key

    async def scan(self, file_content: bytes, filename: str) -> bool:
        """
        Placeholder for cloud scanning
        بديل للفحص السحابي

        In production, implement actual API calls to cloud scanning service
        """
        logger.info(f"Cloud scan stub called for {filename}")
        # TODO: Implement actual cloud scanning API integration
        return True

    async def is_available(self) -> bool:
        """Check if cloud scanner is configured"""
        return self.api_key is not None


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
