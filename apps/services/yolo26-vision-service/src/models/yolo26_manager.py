"""
YOLO26 Model Manager.

Handles loading, caching, and inference for YOLO26 models with support
for TensorRT optimization and async inference.
"""

import asyncio
import base64
import io
import time
from collections import OrderedDict
from contextlib import asynccontextmanager
from enum import Enum, StrEnum
from pathlib import Path
from typing import Any

import numpy as np
import structlog
import torch
from PIL import Image

logger = structlog.get_logger(__name__)


class ModelType(StrEnum):
    """Types of YOLO26 models available."""

    DETECTION = "detection"
    SEGMENTATION = "segmentation"
    CLASSIFICATION = "classification"
    POSE = "pose"


class ModelTask(StrEnum):
    """Specific agricultural tasks for models."""

    PEST_DETECTION = "pest_detection"
    DISEASE_DETECTION = "disease_detection"
    WEED_DETECTION = "weed_detection"
    PLANT_COUNTING = "plant_counting"
    RIPENESS_CLASSIFICATION = "ripeness_classification"
    LEAF_SEGMENTATION = "leaf_segmentation"
    GENERAL_DETECTION = "general_detection"


# Model file mappings for each task
MODEL_FILES: dict[ModelTask, dict[str, str]] = {
    ModelTask.PEST_DETECTION: {
        "n": "yolo26n-pest.pt",
        "s": "yolo26s-pest.pt",
        "m": "yolo26m-pest.pt",
        "l": "yolo26l-pest.pt",
        "x": "yolo26x-pest.pt",
    },
    ModelTask.DISEASE_DETECTION: {
        "n": "yolo26n-disease.pt",
        "s": "yolo26s-disease.pt",
        "m": "yolo26m-disease.pt",
        "l": "yolo26l-disease.pt",
        "x": "yolo26x-disease.pt",
    },
    ModelTask.WEED_DETECTION: {
        "n": "yolo26n-weed.pt",
        "s": "yolo26s-weed.pt",
        "m": "yolo26m-weed.pt",
        "l": "yolo26l-weed.pt",
        "x": "yolo26x-weed.pt",
    },
    ModelTask.PLANT_COUNTING: {
        "n": "yolo26n-plant.pt",
        "s": "yolo26s-plant.pt",
        "m": "yolo26m-plant.pt",
        "l": "yolo26l-plant.pt",
        "x": "yolo26x-plant.pt",
    },
    ModelTask.RIPENESS_CLASSIFICATION: {
        "n": "yolo26n-ripeness-cls.pt",
        "s": "yolo26s-ripeness-cls.pt",
        "m": "yolo26m-ripeness-cls.pt",
        "l": "yolo26l-ripeness-cls.pt",
        "x": "yolo26x-ripeness-cls.pt",
    },
    ModelTask.LEAF_SEGMENTATION: {
        "n": "yolo26n-leaf-seg.pt",
        "s": "yolo26s-leaf-seg.pt",
        "m": "yolo26m-leaf-seg.pt",
        "l": "yolo26l-leaf-seg.pt",
        "x": "yolo26x-leaf-seg.pt",
    },
    ModelTask.GENERAL_DETECTION: {
        "n": "yolo26n.pt",
        "s": "yolo26s.pt",
        "m": "yolo26m.pt",
        "l": "yolo26l.pt",
        "x": "yolo26x.pt",
    },
}


class LRUCache(OrderedDict):
    """LRU cache implementation for models."""

    def __init__(self, maxsize: int = 5):
        super().__init__()
        self.maxsize = maxsize

    def get(self, key: str) -> Any | None:
        """Get item and move to end (most recently used)."""
        if key not in self:
            return None
        self.move_to_end(key)
        return self[key]

    def put(self, key: str, value: Any) -> None:
        """Put item and evict oldest if over capacity."""
        if key in self:
            self.move_to_end(key)
        self[key] = value
        if len(self) > self.maxsize:
            oldest = next(iter(self))
            del self[oldest]
            logger.info("model_evicted", model_key=oldest)


class InferenceResult:
    """Container for inference results."""

    def __init__(
        self,
        boxes: np.ndarray | None = None,
        scores: np.ndarray | None = None,
        class_ids: np.ndarray | None = None,
        masks: np.ndarray | None = None,
        keypoints: np.ndarray | None = None,
        class_probs: np.ndarray | None = None,
        track_ids: np.ndarray | None = None,
        orig_shape: tuple[int, int] | None = None,
        inference_time_ms: float = 0.0,
    ):
        self.boxes = boxes if boxes is not None else np.array([])
        self.scores = scores if scores is not None else np.array([])
        self.class_ids = class_ids if class_ids is not None else np.array([])
        self.masks = masks
        self.keypoints = keypoints
        self.class_probs = class_probs
        self.track_ids = track_ids
        self.orig_shape = orig_shape
        self.inference_time_ms = inference_time_ms

    @property
    def count(self) -> int:
        """Number of detections."""
        return len(self.boxes)

    def filter_by_confidence(self, threshold: float) -> "InferenceResult":
        """Filter results by confidence threshold."""
        if len(self.scores) == 0:
            return self

        mask = self.scores >= threshold
        return InferenceResult(
            boxes=self.boxes[mask] if len(self.boxes) > 0 else self.boxes,
            scores=self.scores[mask],
            class_ids=self.class_ids[mask] if len(self.class_ids) > 0 else self.class_ids,
            masks=self.masks[mask] if self.masks is not None else None,
            track_ids=self.track_ids[mask] if self.track_ids is not None else None,
            orig_shape=self.orig_shape,
            inference_time_ms=self.inference_time_ms,
        )


class YOLO26ModelManager:
    """
    Manager for YOLO26 models.

    Handles model loading, caching, TensorRT optimization, and async inference.
    """

    def __init__(
        self,
        model_base_path: str = "/models",
        cache_size: int = 5,
        device: str = "cuda:0",
        half_precision: bool = True,
        enable_tensorrt: bool = False,
    ):
        self.model_base_path = Path(model_base_path)
        self.device = self._validate_device(device)
        self.half_precision = half_precision and self.device.startswith("cuda")
        self.enable_tensorrt = enable_tensorrt and self.device.startswith("cuda")

        self._model_cache = LRUCache(maxsize=cache_size)
        self._inference_lock = asyncio.Lock()
        self._loading_locks: dict[str, asyncio.Lock] = {}
        self._tracker_states: dict[str, Any] = {}
        self._degraded_mode = False
        self._degraded_tasks: list[str] = []

        logger.info(
            "yolo26_manager_initialized",
            model_base_path=str(self.model_base_path),
            device=self.device,
            half_precision=self.half_precision,
            enable_tensorrt=self.enable_tensorrt,
            cache_size=cache_size,
        )

    def _validate_device(self, device: str) -> str:
        """Validate and return appropriate device."""
        if device.startswith("cuda"):
            if torch.cuda.is_available():
                device_idx = 0
                if ":" in device:
                    try:
                        device_idx = int(device.split(":")[1])
                    except ValueError:
                        device_idx = 0

                if device_idx < torch.cuda.device_count():
                    logger.info(
                        "cuda_device_selected",
                        device=device,
                        gpu_name=torch.cuda.get_device_name(device_idx),
                    )
                    return device
                else:
                    logger.warning(
                        "cuda_device_not_found",
                        requested=device,
                        available=torch.cuda.device_count(),
                    )
                    return "cuda:0" if torch.cuda.device_count() > 0 else "cpu"
            else:
                logger.warning("cuda_not_available", falling_back_to="cpu")
                return "cpu"
        return device

    def _get_model_key(self, task: ModelTask, variant: str) -> str:
        """Generate cache key for a model."""
        return f"{task.value}_{variant}"

    def _get_model_path(self, task: ModelTask, variant: str) -> Path:
        """Get the path for a specific model."""
        model_files = MODEL_FILES.get(task, {})
        filename = model_files.get(variant)
        if not filename:
            raise ValueError(f"No model file for task={task.value}, variant={variant}")
        return self.model_base_path / filename

    async def _get_loading_lock(self, model_key: str) -> asyncio.Lock:
        """Get or create a loading lock for a model."""
        if model_key not in self._loading_locks:
            self._loading_locks[model_key] = asyncio.Lock()
        return self._loading_locks[model_key]

    async def load_model(self, task: ModelTask, variant: str = "m") -> Any:
        """
        Load a YOLO26 model with caching.

        Args:
            task: The model task type
            variant: Model variant (n, s, m, l, x)

        Returns:
            Loaded YOLO model
        """
        model_key = self._get_model_key(task, variant)

        # Check cache first
        cached_model = self._model_cache.get(model_key)
        if cached_model is not None:
            logger.debug("model_cache_hit", model_key=model_key)
            return cached_model

        # Acquire loading lock to prevent duplicate loads
        loading_lock = await self._get_loading_lock(model_key)
        async with loading_lock:
            # Double-check cache after acquiring lock
            cached_model = self._model_cache.get(model_key)
            if cached_model is not None:
                return cached_model

            model_path = self._get_model_path(task, variant)

            logger.info("loading_model", model_key=model_key, path=str(model_path))
            start_time = time.perf_counter()

            try:
                # Import ultralytics here to avoid startup overhead
                from ultralytics import YOLO

                # Load in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                model = await loop.run_in_executor(None, self._load_model_sync, model_path)

                # Apply TensorRT optimization if enabled
                if self.enable_tensorrt:
                    model = await self._optimize_tensorrt(model, model_path)

                # Move to device and set precision
                model.to(self.device)
                if self.half_precision:
                    model.model.half()

                # Cache the model
                self._model_cache.put(model_key, model)

                load_time = (time.perf_counter() - start_time) * 1000
                logger.info(
                    "model_loaded",
                    model_key=model_key,
                    load_time_ms=round(load_time, 2),
                    device=self.device,
                )

                return model

            except FileNotFoundError:
                logger.error("model_file_not_found", path=str(model_path))
                raise
            except Exception as e:
                logger.error("model_load_failed", model_key=model_key, error=str(e))
                raise

    def _load_model_sync(self, model_path: Path) -> Any:
        """Synchronously load a model (for use in executor)."""
        from ultralytics import YOLO

        if not model_path.exists():
            # Determine task and variant from path for logging
            task_info = model_path.stem  # e.g. "yolo26m-pest"
            logger.error(
                "agricultural_model_missing",
                path=str(model_path),
                task=task_info,
                fallback="yolov8m.pt",
                message="DEGRADED: Using generic model without agricultural training. "
                "Detection results will NOT be calibrated for agricultural pest/disease/weed classes.",
            )
            self._degraded_mode = True
            if task_info not in self._degraded_tasks:
                self._degraded_tasks.append(task_info)
            return YOLO("yolov8m.pt")

        return YOLO(str(model_path))

    async def _optimize_tensorrt(self, model: Any, model_path: Path) -> Any:
        """Apply TensorRT optimization to model."""
        try:
            engine_path = model_path.with_suffix(".engine")

            if engine_path.exists():
                logger.info("loading_tensorrt_engine", path=str(engine_path))
                from ultralytics import YOLO

                return YOLO(str(engine_path))

            logger.info("exporting_tensorrt_engine", path=str(engine_path))
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: model.export(
                    format="engine",
                    half=self.half_precision,
                    device=self.device,
                ),
            )

            if engine_path.exists():
                from ultralytics import YOLO

                return YOLO(str(engine_path))

            logger.warning("tensorrt_export_failed", falling_back_to="pytorch")
            return model

        except Exception as e:
            logger.warning("tensorrt_optimization_failed", error=str(e))
            return model

    async def predict(
        self,
        task: ModelTask,
        image: np.ndarray | Image.Image | bytes | str,
        variant: str = "m",
        conf: float = 0.25,
        iou: float = 0.45,
        max_det: int = 300,
        imgsz: int = 640,
        classes: list[int] | None = None,
        agnostic_nms: bool = False,
        retina_masks: bool = True,
    ) -> InferenceResult:
        """
        Run inference on an image.

        Args:
            task: Model task type
            image: Input image (numpy array, PIL Image, bytes, or path)
            variant: Model variant
            conf: Confidence threshold
            iou: IoU threshold for NMS
            max_det: Maximum detections
            imgsz: Input image size
            classes: Filter by class IDs
            agnostic_nms: Class-agnostic NMS
            retina_masks: High-resolution masks for segmentation

        Returns:
            InferenceResult with detections
        """
        model = await self.load_model(task, variant)

        # Convert image to appropriate format
        img = self._prepare_image(image)
        orig_shape = (img.shape[0], img.shape[1]) if isinstance(img, np.ndarray) else img.size[::-1]

        logger.debug(
            "running_inference",
            task=task.value,
            variant=variant,
            image_shape=orig_shape,
        )

        start_time = time.perf_counter()

        # Run inference in thread pool
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: model.predict(
                img,
                conf=conf,
                iou=iou,
                max_det=max_det,
                imgsz=imgsz,
                classes=classes,
                agnostic_nms=agnostic_nms,
                retina_masks=retina_masks,
                verbose=False,
            ),
        )

        inference_time = (time.perf_counter() - start_time) * 1000

        # Parse results
        result = self._parse_results(results[0] if results else None, orig_shape, inference_time)

        logger.debug(
            "inference_complete",
            detections=result.count,
            inference_time_ms=round(inference_time, 2),
        )

        return result

    async def predict_with_tracking(
        self,
        task: ModelTask,
        image: np.ndarray | Image.Image | bytes | str,
        tracker_id: str,
        variant: str = "m",
        conf: float = 0.3,
        iou: float = 0.45,
        max_det: int = 300,
        imgsz: int = 640,
        tracker: str = "bytetrack.yaml",
        persist: bool = True,
    ) -> InferenceResult:
        """
        Run inference with object tracking.

        Args:
            task: Model task type
            image: Input image
            tracker_id: Unique identifier for tracker state
            variant: Model variant
            conf: Confidence threshold
            iou: IoU threshold
            max_det: Maximum detections
            imgsz: Input image size
            tracker: Tracker configuration
            persist: Persist track IDs

        Returns:
            InferenceResult with track IDs
        """
        model = await self.load_model(task, variant)
        img = self._prepare_image(image)
        orig_shape = (img.shape[0], img.shape[1]) if isinstance(img, np.ndarray) else img.size[::-1]

        start_time = time.perf_counter()

        # Run tracking inference
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: model.track(
                img,
                conf=conf,
                iou=iou,
                max_det=max_det,
                imgsz=imgsz,
                tracker=tracker,
                persist=persist,
                verbose=False,
            ),
        )

        inference_time = (time.perf_counter() - start_time) * 1000
        result = self._parse_results(results[0] if results else None, orig_shape, inference_time)

        return result

    def _prepare_image(self, image: np.ndarray | Image.Image | bytes | str) -> np.ndarray:
        """Convert various image formats to numpy array."""
        if isinstance(image, np.ndarray):
            return image
        elif isinstance(image, Image.Image):
            return np.array(image)
        elif isinstance(image, bytes):
            pil_image = Image.open(io.BytesIO(image))
            return np.array(pil_image)
        elif isinstance(image, str):
            if image.startswith("data:image"):
                # Base64 encoded image
                base64_data = image.split(",")[1] if "," in image else image
                image_bytes = base64.b64decode(base64_data)
                pil_image = Image.open(io.BytesIO(image_bytes))
                return np.array(pil_image)
            else:
                # File path
                pil_image = Image.open(image)
                return np.array(pil_image)
        else:
            raise ValueError(f"Unsupported image type: {type(image)}")

    def _parse_results(
        self,
        result: Any,
        orig_shape: tuple[int, int],
        inference_time: float,
    ) -> InferenceResult:
        """Parse YOLO results into InferenceResult."""
        if result is None:
            return InferenceResult(orig_shape=orig_shape, inference_time_ms=inference_time)

        boxes = np.array([])
        scores = np.array([])
        class_ids = np.array([])
        masks = None
        track_ids = None
        class_probs = None

        # Extract boxes
        if result.boxes is not None and len(result.boxes) > 0:
            boxes = result.boxes.xyxy.cpu().numpy()
            scores = result.boxes.conf.cpu().numpy()
            class_ids = result.boxes.cls.cpu().numpy().astype(int)

            # Extract track IDs if available
            if hasattr(result.boxes, "id") and result.boxes.id is not None:
                track_ids = result.boxes.id.cpu().numpy().astype(int)

        # Extract masks for segmentation
        if result.masks is not None and len(result.masks) > 0:
            masks = result.masks.data.cpu().numpy()

        # Extract class probabilities for classification
        if result.probs is not None:
            class_probs = result.probs.data.cpu().numpy()

        return InferenceResult(
            boxes=boxes,
            scores=scores,
            class_ids=class_ids,
            masks=masks,
            track_ids=track_ids,
            class_probs=class_probs,
            orig_shape=orig_shape,
            inference_time_ms=inference_time,
        )

    def is_model_loaded(self, task: ModelTask, variant: str = "m") -> bool:
        """Check if a model is loaded in cache."""
        model_key = self._get_model_key(task, variant)
        return model_key in self._model_cache

    def get_loaded_models(self) -> list[str]:
        """Get list of currently loaded model keys."""
        return list(self._model_cache.keys())

    def clear_cache(self) -> None:
        """Clear all cached models."""
        self._model_cache.clear()
        self._tracker_states.clear()
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        logger.info("model_cache_cleared")

    def reset_tracker(self, tracker_id: str) -> None:
        """Reset a specific tracker state."""
        if tracker_id in self._tracker_states:
            del self._tracker_states[tracker_id]
            logger.debug("tracker_reset", tracker_id=tracker_id)

    @property
    def gpu_available(self) -> bool:
        """Check if GPU is available."""
        return torch.cuda.is_available()

    @property
    def gpu_memory_info(self) -> dict[str, float] | None:
        """Get GPU memory information."""
        if not torch.cuda.is_available():
            return None

        try:
            device_idx = int(self.device.split(":")[1]) if ":" in self.device else 0
            allocated = torch.cuda.memory_allocated(device_idx) / 1024**3
            reserved = torch.cuda.memory_reserved(device_idx) / 1024**3
            total = torch.cuda.get_device_properties(device_idx).total_memory / 1024**3
            return {
                "allocated_gb": round(allocated, 2),
                "reserved_gb": round(reserved, 2),
                "total_gb": round(total, 2),
                "free_gb": round(total - allocated, 2),
            }
        except Exception:
            return None


# Singleton instance
_manager_instance: YOLO26ModelManager | None = None


def get_model_manager() -> YOLO26ModelManager:
    """Get the singleton model manager instance."""
    global _manager_instance
    if _manager_instance is None:
        from src.core.config import settings

        _manager_instance = YOLO26ModelManager(
            model_base_path=settings.model_base_path,
            cache_size=settings.model_cache_size,
            device=settings.device,
            half_precision=settings.half_precision,
            enable_tensorrt=settings.enable_tensorrt,
        )
    return _manager_instance


@asynccontextmanager
async def model_manager_context():
    """Context manager for model manager lifecycle."""
    manager = get_model_manager()
    try:
        yield manager
    finally:
        manager.clear_cache()
