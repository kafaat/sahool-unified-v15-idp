"""
QR Code Generator for Produce Batch Traceability
مولد رمز QR لتتبع دفعات المنتجات

Generates QR codes containing batch information for scanning
at any point in the supply chain or by consumers.

ينشئ رموز QR تحتوي على معلومات الدفعة للمسح
في أي نقطة من سلسلة التوريد أو من قبل المستهلكين.
"""

from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from io import BytesIO
from urllib.parse import urlencode

from .models import (
    ProduceBatch,
    QRCodeData,
)


class QRFormat(StrEnum):
    """QR code output formats"""

    PNG = "png"
    SVG = "svg"
    BASE64_PNG = "base64_png"
    BASE64_SVG = "base64_svg"


class QRSize(StrEnum):
    """QR code size presets"""

    SMALL = "small"  # 128x128 - for labels
    MEDIUM = "medium"  # 256x256 - for boxes
    LARGE = "large"  # 512x512 - for posters
    XLARGE = "xlarge"  # 1024x1024 - for print


# Size mappings in pixels
QR_SIZE_PIXELS = {
    QRSize.SMALL: 128,
    QRSize.MEDIUM: 256,
    QRSize.LARGE: 512,
    QRSize.XLARGE: 1024,
}


@dataclass
class QRGenerationConfig:
    """Configuration for QR code generation - إعدادات إنشاء رمز QR"""

    # Base URL for verification endpoint
    base_url: str = "https://trace.sahool.app"

    def __post_init__(self):
        """Validate base_url to prevent SSRF."""
        from urllib.parse import urlparse

        parsed = urlparse(self.base_url)
        if parsed.scheme not in ("http", "https"):
            raise ValueError(f"base_url must use http/https, got: {parsed.scheme}")
        if not parsed.hostname:
            raise ValueError("base_url must have a valid hostname")

    # Output settings
    format: QRFormat = QRFormat.PNG
    size: QRSize = QRSize.MEDIUM

    # Visual customization
    foreground_color: str = "#000000"  # Black
    background_color: str = "#FFFFFF"  # White
    logo_url: str | None = None  # Logo to embed in center
    logo_size_ratio: float = 0.25  # Logo size as ratio of QR size

    # Error correction level (L, M, Q, H)
    # Higher = more redundancy, more data, larger QR
    error_correction: str = "M"

    # Include border (quiet zone)
    border_modules: int = 4


@dataclass
class GeneratedQRCode:
    """Result of QR code generation - نتيجة إنشاء رمز QR"""

    batch_id: str
    batch_code: str

    # QR data
    qr_data: str  # Data encoded in QR
    verification_url: str  # Full URL for verification

    # Generated image
    image_data: bytes = field(default=b"", repr=False)
    image_base64: str = ""
    image_format: QRFormat = QRFormat.PNG

    # Metadata
    size_pixels: int = 256
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Checksum for verification
    checksum: str = ""


class QRCodeGenerator:
    """
    QR Code Generator for batch traceability
    مولد رمز QR لتتبع الدفعات

    Generates QR codes that link to product journey information.
    ينشئ رموز QR ترتبط بمعلومات رحلة المنتج.
    """

    def __init__(self, config: QRGenerationConfig | None = None):
        """
        Initialize QR generator.

        Args:
            config: QR generation configuration
        """
        self.config = config or QRGenerationConfig()
        self._qrcode_available = self._check_qrcode_library()

    def _check_qrcode_library(self) -> bool:
        """Check if qrcode library is available"""
        try:
            import qrcode  # noqa: F401

            return True
        except ImportError:
            return False

    def generate_for_batch(
        self,
        batch: ProduceBatch,
        config: QRGenerationConfig | None = None,
    ) -> GeneratedQRCode:
        """
        Generate QR code for a produce batch.
        إنشاء رمز QR لدفعة منتج.

        Args:
            batch: The produce batch
            config: Optional override configuration

        Returns:
            Generated QR code with image data
        """
        cfg = config or self.config

        # Build verification URL
        verification_url = self._build_verification_url(batch, cfg)

        # Create QR data structure
        qr_data = self._build_qr_data(batch, verification_url)

        # Generate QR code image
        if self._qrcode_available:
            image_data, image_base64 = self._generate_qr_image(qr_data, cfg)
        else:
            # Fallback: return URL-based placeholder
            image_data = b""
            image_base64 = ""

        # Calculate checksum
        checksum = self._calculate_checksum(batch.id, batch.batch_code, qr_data)

        return GeneratedQRCode(
            batch_id=batch.id,
            batch_code=batch.batch_code,
            qr_data=qr_data,
            verification_url=verification_url,
            image_data=image_data,
            image_base64=image_base64,
            image_format=cfg.format,
            size_pixels=QR_SIZE_PIXELS[cfg.size],
            checksum=checksum,
        )

    def generate_bulk(
        self,
        batches: list[ProduceBatch],
        config: QRGenerationConfig | None = None,
    ) -> list[GeneratedQRCode]:
        """
        Generate QR codes for multiple batches.
        إنشاء رموز QR لدفعات متعددة.

        Args:
            batches: List of produce batches
            config: Optional override configuration

        Returns:
            List of generated QR codes
        """
        return [self.generate_for_batch(batch, config) for batch in batches]

    def generate_from_data(
        self,
        qr_code_data: QRCodeData,
        config: QRGenerationConfig | None = None,
    ) -> GeneratedQRCode:
        """
        Generate QR code from QRCodeData object.
        إنشاء رمز QR من كائن QRCodeData.

        Args:
            qr_code_data: Pre-built QR code data
            config: Optional override configuration

        Returns:
            Generated QR code with image data
        """
        cfg = config or self.config

        # Use compact string format
        qr_data = qr_code_data.to_compact_string()

        # Generate QR code image
        if self._qrcode_available:
            image_data, image_base64 = self._generate_qr_image(qr_data, cfg)
        else:
            image_data = b""
            image_base64 = ""

        # Calculate checksum
        checksum = self._calculate_checksum(
            qr_code_data.batch_id,
            qr_code_data.batch_code,
            qr_data,
        )

        return GeneratedQRCode(
            batch_id=qr_code_data.batch_id,
            batch_code=qr_code_data.batch_code,
            qr_data=qr_data,
            verification_url=qr_code_data.verification_url,
            image_data=image_data,
            image_base64=image_base64,
            image_format=cfg.format,
            size_pixels=QR_SIZE_PIXELS[cfg.size],
            checksum=checksum,
        )

    def _build_verification_url(
        self,
        batch: ProduceBatch,
        config: QRGenerationConfig,
    ) -> str:
        """Build the verification URL for a batch"""
        # URL format: https://trace.sahool.app/verify/{batch_code}?sig={signature}
        signature = self._generate_signature(batch)
        params = urlencode(
            {
                "sig": signature,
                "lang": "ar",  # Default to Arabic
            }
        )
        return f"{config.base_url}/verify/{batch.batch_code}?{params}"

    def _build_qr_data(
        self,
        batch: ProduceBatch,
        verification_url: str,
    ) -> str:
        """Build the data string to encode in QR"""
        # Use JSON format for rich data encoding
        data = {
            "v": 1,  # Version
            "t": "SAHOOL",  # Type identifier
            "b": batch.batch_code,
            "p": batch.product_name_en[:30],  # Truncate for QR size
            "h": batch.harvest_date.strftime("%Y-%m-%d") if batch.harvest_date else "",
            "u": verification_url,
        }
        return json.dumps(data, separators=(",", ":"))

    def _generate_qr_image(
        self,
        data: str,
        config: QRGenerationConfig,
    ) -> tuple[bytes, str]:
        """Generate the actual QR code image"""
        try:
            import qrcode
            from qrcode.constants import (
                ERROR_CORRECT_H,
                ERROR_CORRECT_L,
                ERROR_CORRECT_M,
                ERROR_CORRECT_Q,
            )
        except ImportError:
            return b"", ""

        # Map error correction levels
        error_levels = {
            "L": ERROR_CORRECT_L,
            "M": ERROR_CORRECT_M,
            "Q": ERROR_CORRECT_Q,
            "H": ERROR_CORRECT_H,
        }
        error_level = error_levels.get(config.error_correction, ERROR_CORRECT_M)

        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=error_level,
            box_size=10,
            border=config.border_modules,
        )
        qr.add_data(data)
        qr.make(fit=True)

        # Generate image
        size = QR_SIZE_PIXELS[config.size]

        if config.format in (QRFormat.SVG, QRFormat.BASE64_SVG):
            # SVG output
            try:
                from qrcode.image.svg import SvgImage

                img = qr.make_image(
                    image_factory=SvgImage,
                    fill_color=config.foreground_color,
                    back_color=config.background_color,
                )
                buffer = BytesIO()
                img.save(buffer)
                image_data = buffer.getvalue()
            except ImportError:
                # Fallback to PNG
                img = qr.make_image(
                    fill_color=config.foreground_color,
                    back_color=config.background_color,
                )
                img = img.resize((size, size))
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                image_data = buffer.getvalue()
        else:
            # PNG output
            img = qr.make_image(
                fill_color=config.foreground_color,
                back_color=config.background_color,
            )
            # Resize to target size
            img = img.resize((size, size))

            buffer = BytesIO()
            img.save(buffer, format="PNG")
            image_data = buffer.getvalue()

        # Generate base64
        image_base64 = base64.b64encode(image_data).decode("utf-8")

        return image_data, image_base64

    def _generate_signature(self, batch: ProduceBatch) -> str:
        """Generate a verification signature for the batch"""
        # Create signature from batch data
        data_to_sign = f"{batch.id}|{batch.batch_code}|{batch.tenant_id}"
        return hashlib.sha256(data_to_sign.encode()).hexdigest()[:16]

    def _calculate_checksum(
        self,
        batch_id: str,
        batch_code: str,
        qr_data: str,
    ) -> str:
        """Calculate checksum for QR data verification using SHA256"""
        data = f"{batch_id}|{batch_code}|{qr_data}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]


# ─────────────────────────────────────────────────────────────────────────────
# Label Generator - مولد الملصقات
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class LabelData:
    """Data for printing product labels - بيانات طباعة ملصقات المنتج"""

    batch_code: str
    product_name_en: str
    product_name_ar: str
    variety_en: str
    variety_ar: str
    producer_name_en: str
    producer_name_ar: str
    harvest_date: str
    expiry_date: str | None = None
    weight: str | None = None  # e.g., "500g"
    quality_grade: str = ""
    certifications: list[str] = field(default_factory=list)  # Certification logos/names
    qr_code_base64: str = ""


class LabelGenerator:
    """
    Generate printable labels with QR codes
    إنشاء ملصقات قابلة للطباعة مع رموز QR
    """

    def __init__(self, qr_generator: QRCodeGenerator | None = None):
        self.qr_generator = qr_generator or QRCodeGenerator()

    def generate_label_data(
        self,
        batch: ProduceBatch,
        producer_name_en: str = "",
        producer_name_ar: str = "",
        certifications: list[str] | None = None,
    ) -> LabelData:
        """
        Generate label data for a batch.
        إنشاء بيانات الملصق لدفعة.

        Args:
            batch: The produce batch
            producer_name_en: Producer name in English
            producer_name_ar: Producer name in Arabic
            certifications: List of certification names

        Returns:
            Label data ready for printing
        """
        # Generate QR code
        qr_config = QRGenerationConfig(size=QRSize.SMALL)
        qr_result = self.qr_generator.generate_for_batch(batch, qr_config)

        return LabelData(
            batch_code=batch.batch_code,
            product_name_en=batch.product_name_en,
            product_name_ar=batch.product_name_ar,
            variety_en=batch.variety_en,
            variety_ar=batch.variety_ar,
            producer_name_en=producer_name_en,
            producer_name_ar=producer_name_ar,
            harvest_date=batch.harvest_date.strftime("%Y-%m-%d") if batch.harvest_date else "",
            expiry_date=batch.expiry_date.strftime("%Y-%m-%d") if batch.expiry_date else None,
            weight=f"{batch.quantity} {batch.quantity_unit}" if batch.quantity else None,
            quality_grade=batch.quality_grade.value if batch.quality_grade else "",
            certifications=certifications or [],
            qr_code_base64=qr_result.image_base64,
        )

    def generate_html_label(
        self,
        label_data: LabelData,
        width_mm: int = 50,
        height_mm: int = 30,
    ) -> str:
        """
        Generate HTML representation of a label.
        إنشاء تمثيل HTML للملصق.

        Args:
            label_data: The label data
            width_mm: Label width in mm
            height_mm: Label height in mm

        Returns:
            HTML string for the label
        """
        qr_img = ""
        if label_data.qr_code_base64:
            qr_img = f'<img src="data:image/png;base64,{label_data.qr_code_base64}" alt="QR Code" />'

        expiry_html = ""
        if label_data.expiry_date:
            expiry_html = f"""
            <div class="expiry">
                <span class="label">Expiry/انتهاء:</span>
                <span class="value">{label_data.expiry_date}</span>
            </div>
            """

        return f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <style>
                .label {{
                    width: {width_mm}mm;
                    height: {height_mm}mm;
                    padding: 2mm;
                    border: 1px solid #000;
                    font-family: Arial, sans-serif;
                    font-size: 8pt;
                    display: flex;
                    flex-direction: row;
                }}
                .qr-section {{
                    width: 30%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                .qr-section img {{
                    max-width: 100%;
                    max-height: 100%;
                }}
                .info-section {{
                    width: 70%;
                    padding-left: 2mm;
                }}
                .product-name {{
                    font-weight: bold;
                    font-size: 10pt;
                    margin-bottom: 1mm;
                }}
                .product-name-ar {{
                    font-size: 9pt;
                }}
                .field {{
                    margin: 0.5mm 0;
                }}
                .label-text {{
                    color: #666;
                }}
                .batch-code {{
                    font-family: monospace;
                    font-size: 7pt;
                    margin-top: 1mm;
                }}
            </style>
        </head>
        <body>
            <div class="label">
                <div class="qr-section">
                    {qr_img}
                </div>
                <div class="info-section">
                    <div class="product-name">{label_data.product_name_en}</div>
                    <div class="product-name-ar">{label_data.product_name_ar}</div>
                    <div class="field">
                        <span class="label-text">Harvest/الحصاد:</span> {label_data.harvest_date}
                    </div>
                    {expiry_html}
                    <div class="field">
                        <span class="label-text">Producer/المنتج:</span> {label_data.producer_name_ar}
                    </div>
                    <div class="batch-code">{label_data.batch_code}</div>
                </div>
            </div>
        </body>
        </html>
        """


# ─────────────────────────────────────────────────────────────────────────────
# Utility Functions - دوال مساعدة
# ─────────────────────────────────────────────────────────────────────────────


def generate_batch_code(
    product_code: str,
    year: int,
    sequence: int,
    farm_code: str | None = None,
) -> str:
    """
    Generate a human-readable batch code.
    إنشاء رمز دفعة قابل للقراءة.

    Format: [PRODUCT]-[FARM]-[YEAR]-[SEQ]
    Example: WH-ALR-2025-001 (Wheat from Al-Rashid farm, 2025, sequence 001)

    Args:
        product_code: 2-3 letter product code (e.g., "WH" for wheat)
        year: Year of harvest
        sequence: Sequential batch number
        farm_code: Optional 3-letter farm code

    Returns:
        Formatted batch code
    """
    year_short = str(year)[-2:]  # Last 2 digits
    seq_padded = str(sequence).zfill(3)

    if farm_code:
        return f"{product_code.upper()}-{farm_code.upper()}-{year_short}-{seq_padded}"
    return f"{product_code.upper()}-{year_short}-{seq_padded}"


def decode_qr_data(qr_data: str) -> dict | None:
    """
    Decode QR data string back to dictionary.
    فك تشفير سلسلة بيانات QR إلى قاموس.

    Args:
        qr_data: The QR data string

    Returns:
        Decoded dictionary or None if invalid
    """
    try:
        return json.loads(qr_data)
    except json.JSONDecodeError:
        # Try parsing as compact SAHOOL format
        if qr_data.startswith("SAHOOL|"):
            parts = qr_data.split("|")
            if len(parts) >= 5:
                return {
                    "t": parts[0],
                    "b": parts[1],
                    "p": parts[2],
                    "h": parts[3],
                    "u": parts[4],
                }
        return None


def verify_qr_checksum(generated_qr: GeneratedQRCode) -> bool:
    """
    Verify the checksum of a generated QR code.
    التحقق من المجموع الاختباري لرمز QR المولد.

    Args:
        generated_qr: The generated QR code object

    Returns:
        True if checksum is valid
    """
    data = f"{generated_qr.batch_id}|{generated_qr.batch_code}|{generated_qr.qr_data}"
    expected_checksum = hashlib.sha256(data.encode()).hexdigest()[:32]
    return generated_qr.checksum == expected_checksum
