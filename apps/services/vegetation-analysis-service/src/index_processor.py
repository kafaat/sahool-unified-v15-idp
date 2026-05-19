"""
Index Processor
معالج المؤشرات

Converts raw Sentinel-2 band bytes (B02/B03/B04/B08/SCL) into
NDVI / EVI / LAI / NDWI statistics plus GeoTIFF and PNG thumbnail.

Band layout from the evalscript in cdse_client.py:
  channel 0 → B02 (Blue)
  channel 1 → B03 (Green)
  channel 2 → B04 (Red)
  channel 3 → B08 (NIR)
  channel 4 → SCL (Scene Classification Layer)

SCL cloud classes (exclude from valid pixels):
  3  → Cloud shadows
  8  → Medium probability cloud
  9  → High probability cloud
  10 → Thin cirrus
"""

from __future__ import annotations

import io
import warnings
from dataclasses import dataclass
from datetime import date
from typing import Any

import numpy as np
import structlog

logger = structlog.get_logger(__name__)

# SCL classes treated as cloud/shadow → masked out
_CLOUD_SCL = {3, 8, 9, 10}


@dataclass
class IndexStats:
    mean: float
    min: float
    max: float
    std: float


@dataclass
class ProcessedField:
    field_id: str
    tenant_id: str
    acquisition_date: date
    cloud_cover_percent: float
    ndvi: IndexStats
    evi: IndexStats
    lai: IndexStats
    ndwi: IndexStats
    geotiff_bytes: bytes | None
    png_bytes: bytes | None

    def to_dict(self) -> dict[str, Any]:
        def _s(s: IndexStats, prefix: str) -> dict:
            return {
                f"{prefix}_mean": s.mean,
                f"{prefix}_min": s.min,
                f"{prefix}_max": s.max,
                f"{prefix}_std": s.std,
            }

        return {
            "cloud_cover_percent": self.cloud_cover_percent,
            **_s(self.ndvi, "ndvi"),
            **_s(self.evi, "evi"),
            **_s(self.lai, "lai"),
            **_s(self.ndwi, "ndwi"),
        }


class IndexProcessor:
    """
    Processes raw band TIFF bytes into vegetation index statistics.
    Pure numpy — no sentinelhub dependency at runtime.
    """

    # ------------------------------------------------------------------ #
    # Main entry point                                                     #
    # ------------------------------------------------------------------ #

    def process(
        self,
        field_id: str,
        tenant_id: str,
        acquisition_date: date,
        tiff_bytes: bytes,
    ) -> ProcessedField | None:
        """
        Parse tiff_bytes → band arrays → compute indices → stats + assets.
        Returns None if the data cannot be parsed.
        """
        bands = self._parse_tiff(tiff_bytes)
        if bands is None:
            return None

        b02, b03, b04, b08, scl = (
            bands[..., 0].astype(np.float32),
            bands[..., 1].astype(np.float32),
            bands[..., 2].astype(np.float32),
            bands[..., 3].astype(np.float32),
            bands[..., 4],
        )

        # Cloud mask: True where pixel is valid (not cloud/shadow)
        cloud_mask = np.zeros_like(scl, dtype=bool)
        for cls in _CLOUD_SCL:
            cloud_mask |= scl == cls
        valid_mask = ~cloud_mask

        total_pixels = scl.size
        cloud_pixels = int(cloud_mask.sum())
        cloud_cover_pct = (cloud_pixels / total_pixels * 100.0) if total_pixels > 0 else 0.0

        # Compute indices (all pixels, cloud or not — store full array)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            ndvi = self._ndvi(b04, b08)
            evi = self._evi(b02, b04, b08)
            lai = self._lai(ndvi)
            ndwi = self._ndwi(b03, b08)

        # Stats over valid (non-cloud) pixels only
        def _stats(arr: np.ndarray) -> IndexStats:
            masked = arr[valid_mask] if valid_mask.any() else arr.flatten()
            # Clip to expected physical range to remove outliers
            masked = masked[np.isfinite(masked)]
            if len(masked) == 0:
                return IndexStats(0.0, 0.0, 0.0, 0.0)
            return IndexStats(
                mean=float(np.mean(masked)),
                min=float(np.min(masked)),
                max=float(np.max(masked)),
                std=float(np.std(masked)),
            )

        geotiff_bytes = self._make_geotiff(ndvi, evi, lai, ndwi)
        png_bytes = self._make_thumbnail(ndvi)

        return ProcessedField(
            field_id=field_id,
            tenant_id=tenant_id,
            acquisition_date=acquisition_date,
            cloud_cover_percent=round(cloud_cover_pct, 2),
            ndvi=_stats(ndvi),
            evi=_stats(evi),
            lai=_stats(lai),
            ndwi=_stats(ndwi),
            geotiff_bytes=geotiff_bytes,
            png_bytes=png_bytes,
        )

    # ------------------------------------------------------------------ #
    # Index formulas                                                       #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _ndvi(red: np.ndarray, nir: np.ndarray) -> np.ndarray:
        denom = nir + red
        with np.errstate(invalid="ignore", divide="ignore"):
            result = np.where(denom != 0, (nir - red) / denom, 0.0)
        return np.clip(result, -1.0, 1.0)

    @staticmethod
    def _evi(blue: np.ndarray, red: np.ndarray, nir: np.ndarray) -> np.ndarray:
        denom = nir + 6.0 * red - 7.5 * blue + 1.0
        with np.errstate(invalid="ignore", divide="ignore"):
            result = np.where(denom != 0, 2.5 * (nir - red) / denom, 0.0)
        return np.clip(result, -1.0, 1.0)

    @staticmethod
    def _lai(ndvi: np.ndarray) -> np.ndarray:
        # Simplified empirical: LAI = 0.57 * exp(2.33 * NDVI)
        result = 0.57 * np.exp(2.33 * ndvi)
        return np.clip(result, 0.0, 10.0)

    @staticmethod
    def _ndwi(green: np.ndarray, nir: np.ndarray) -> np.ndarray:
        denom = green + nir
        with np.errstate(invalid="ignore", divide="ignore"):
            result = np.where(denom != 0, (green - nir) / denom, 0.0)
        return np.clip(result, -1.0, 1.0)

    # ------------------------------------------------------------------ #
    # TIFF parsing (via rasterio if available, else raw numpy)             #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _parse_tiff(tiff_bytes: bytes) -> np.ndarray | None:
        """
        Parse multi-band TIFF bytes → (H, W, 5) float32 array.
        Tries rasterio first, then falls back to a minimal TIFF reader.
        """
        try:
            import rasterio
            from rasterio.io import MemoryFile

            with MemoryFile(tiff_bytes) as mf:
                with mf.open() as ds:
                    data = ds.read()  # (bands, H, W)
                    return np.transpose(data, (1, 2, 0)).astype(np.float32)
        except ImportError:
            pass
        except Exception as exc:
            logger.error("tiff_parse_rasterio_error", error=str(exc))
            return None

        # Minimal fallback using tifffile if available
        try:
            import tifffile

            arr = tifffile.imread(io.BytesIO(tiff_bytes))
            if arr.ndim == 2:
                arr = arr[..., np.newaxis]
            elif arr.ndim == 3 and arr.shape[0] < arr.shape[-1]:
                # (bands, H, W) → (H, W, bands)
                arr = np.transpose(arr, (1, 2, 0))
            return arr.astype(np.float32)
        except ImportError:
            pass
        except Exception as exc:
            logger.error("tiff_parse_tifffile_error", error=str(exc))

        logger.warning("tiff_parse_no_library", bytes_len=len(tiff_bytes))
        return None

    # ------------------------------------------------------------------ #
    # Asset generation                                                     #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _make_geotiff(
        ndvi: np.ndarray,
        evi: np.ndarray,
        lai: np.ndarray,
        ndwi: np.ndarray,
    ) -> bytes | None:
        """
        Pack 4 index bands into an in-memory GeoTIFF (float32).
        Returns None if rasterio is not installed.
        """
        try:
            import rasterio
            from rasterio.io import MemoryFile
            from rasterio.transform import from_bounds

            h, w = ndvi.shape
            buf = io.BytesIO()
            with MemoryFile() as mf:
                with mf.open(
                    driver="GTiff",
                    height=h,
                    width=w,
                    count=4,
                    dtype="float32",
                ) as ds:
                    ds.write(ndvi.astype(np.float32), 1)
                    ds.write(evi.astype(np.float32), 2)
                    ds.write(lai.astype(np.float32), 3)
                    ds.write(ndwi.astype(np.float32), 4)
                return mf.read()
        except ImportError:
            return None
        except Exception as exc:
            logger.warning("geotiff_generation_error", error=str(exc))
            return None

    @staticmethod
    def _make_thumbnail(ndvi: np.ndarray) -> bytes | None:
        """
        Render NDVI as a colour-mapped PNG (green=healthy, red=stressed).
        Returns None if Pillow is not installed.
        """
        try:
            from PIL import Image

            # Normalise NDVI [-1, 1] → [0, 255]
            normalised = ((ndvi + 1.0) / 2.0 * 255.0).clip(0, 255).astype(np.uint8)
            # Apply a simple green-red colourmap
            r = (255 - normalised).astype(np.uint8)
            g = normalised.astype(np.uint8)
            b = np.zeros_like(r)
            rgb = np.stack([r, g, b], axis=-1)
            img = Image.fromarray(rgb, mode="RGB")
            buf = io.BytesIO()
            img.save(buf, format="PNG", optimize=True)
            return buf.getvalue()
        except ImportError:
            return None
        except Exception as exc:
            logger.warning("thumbnail_generation_error", error=str(exc))
            return None
