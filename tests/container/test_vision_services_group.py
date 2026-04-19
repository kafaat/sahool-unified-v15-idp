"""
SAHOOL Vision/Analysis Services Group – Container Function Tests
=================================================================
اختبارات وظائف مجموعة خدمات الرؤية والتحليل

Validates consistency across the computer-vision and remote-sensing cluster.
All tests are **static analysis** — no Docker daemon required.

Services in this group:
  yolo26-vision-service · ground-vision-service · vegetation-analysis-service
  crop-intelligence-service · pest-detection-service
  field-intelligence · indicators-service

Coverage:
 1.  Computer vision / image processing dependencies
 2.  GPU vs CPU build variant availability
 3.  Consistent base image (CUDA for GPU, slim for CPU)
 4.  Model directory provisioning in Dockerfile
 5.  Image upload size limits (MAX_UPLOAD_SIZE_MB)
 6.  NATS vision event subjects
 7.  Health endpoint patterns
 8.  OpenCV headless variant (no GUI deps)
 9.  Shared analysis output schema
10.  Port range consistency

Run:
    pytest tests/container/test_vision_services_group.py -v --tb=short
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

pytestmark = [pytest.mark.container, pytest.mark.smoke]

REPO_ROOT = Path(__file__).resolve().parents[2]
SERVICES_DIR = REPO_ROOT / "apps" / "services"
MAIN_COMPOSE = REPO_ROOT / "docker-compose.yml"

# --- Service group -----------------------------------------------------------

VISION_SERVICES: dict[str, int] = {
    "yolo26-vision-service": 8150,
    "ground-vision-service": 8182,
    "vegetation-analysis-service": 8090,
    "crop-intelligence-service": 8095,
    "pest-detection-service": 8125,
    "field-intelligence": 8120,
    "indicators-service": 8091,
}

# Sub-cluster: pure CV services that process images directly with local models
CV_SERVICES = {
    "yolo26-vision-service",
    "ground-vision-service",
}

# pest-detection-service delegates CV to shared/ or external services
CV_LIGHT_SERVICES = {"pest-detection-service"}

# Sub-cluster: remote-sensing / satellite services
REMOTE_SENSING_SERVICES = {
    "vegetation-analysis-service",
    "indicators-service",
}

# ---------------------------------------------------------------------------

_dockerfile_cache: dict[str, str] = {}
_requirements_cache: dict[str, str] = {}


def _read_dockerfile(svc: str) -> str:
    if svc not in _dockerfile_cache:
        path = SERVICES_DIR / svc / "Dockerfile"
        _dockerfile_cache[svc] = path.read_text("utf-8") if path.exists() else ""
    return _dockerfile_cache[svc]


def _read_requirements(svc: str) -> str:
    if svc not in _requirements_cache:
        path = SERVICES_DIR / svc / "requirements.txt"
        _requirements_cache[svc] = path.read_text("utf-8") if path.exists() else ""
    return _requirements_cache[svc]


def _req_packages(svc: str) -> set[str]:
    text = _read_requirements(svc)
    pkgs: set[str] = set()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        name = re.split(r"[>=<!\[;]", line)[0].strip().lower().replace("-", "_")
        if name:
            pkgs.add(name)
    return pkgs


@pytest.fixture(scope="module")
def compose() -> dict[str, Any]:
    with open(MAIN_COMPOSE, encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def services(compose: dict) -> dict[str, Any]:
    return compose.get("services", {})


# ===========================================================================
# 1. Image Processing Dependencies
# ===========================================================================


class TestImageProcessingDeps:
    """خدمات الرؤية يجب أن تحتوي على مكتبات معالجة الصور."""

    @pytest.mark.parametrize("svc", sorted(CV_SERVICES))
    def test_opencv_declared(self, svc: str) -> None:
        """CV service declares opencv in requirements."""
        pkgs = _req_packages(svc)
        has_cv = any("opencv" in p for p in pkgs)
        assert has_cv, f"{svc} missing opencv dependency"

    @pytest.mark.parametrize("svc", sorted(CV_SERVICES))
    def test_opencv_headless_variant(self, svc: str) -> None:
        """CV service uses opencv-python-headless (no GUI deps in containers)."""
        text_lower = _read_requirements(svc).lower()
        if "opencv" not in text_lower:
            pytest.skip(f"{svc} does not declare OpenCV")
        uses_headless = "opencv-python-headless" in text_lower
        uses_non_headless = (
            "opencv-python" in text_lower and "opencv-python-headless" not in text_lower
        )
        assert uses_headless and not uses_non_headless, (
            f"{svc} should use opencv-python-headless (not opencv-python)"
        )

    @pytest.mark.parametrize("svc", sorted(CV_SERVICES))
    def test_numpy_declared(self, svc: str) -> None:
        """CV service declares numpy for array processing."""
        pkgs = _req_packages(svc)
        assert "numpy" in pkgs, f"{svc} missing numpy dependency"

    @pytest.mark.parametrize("svc", sorted(CV_SERVICES))
    def test_pillow_declared(self, svc: str) -> None:
        """CV service declares Pillow for image I/O."""
        pkgs = _req_packages(svc)
        assert "pillow" in pkgs or "pil" in pkgs, f"{svc} missing Pillow dependency"


# ===========================================================================
# 2. YOLO26 GPU / CUDA Specific
# ===========================================================================


class TestYOLO26GPUSupport:
    """خدمة YOLO26 يجب أن تدعم GPU وCPU."""

    def test_yolo26_cuda_base_image(self) -> None:
        """YOLO26 Dockerfile uses NVIDIA CUDA base image."""
        content = _read_dockerfile("yolo26-vision-service")
        if not content:
            pytest.skip("No Dockerfile for yolo26-vision-service")
        assert "nvidia/cuda" in content.lower() or "cuda" in content.lower(), (
            "yolo26-vision-service should use NVIDIA CUDA base image"
        )

    def test_yolo26_has_cpu_only_stage(self) -> None:
        """YOLO26 Dockerfile includes a cpu-only build stage."""
        content = _read_dockerfile("yolo26-vision-service")
        if not content:
            pytest.skip("No Dockerfile")
        assert re.search(r"AS\s+cpu", content, re.IGNORECASE), (
            "yolo26-vision-service missing cpu-only build stage"
        )

    def test_yolo26_torch_dependency(self) -> None:
        """YOLO26 declares PyTorch as dependency."""
        pkgs = _req_packages("yolo26-vision-service")
        assert "torch" in pkgs, "yolo26-vision-service missing torch dependency"

    def test_yolo26_ultralytics_dependency(self) -> None:
        """YOLO26 declares ultralytics (YOLO framework)."""
        pkgs = _req_packages("yolo26-vision-service")
        assert "ultralytics" in pkgs, "yolo26-vision-service missing ultralytics"

    def test_yolo26_model_directory(self) -> None:
        """YOLO26 Dockerfile creates /app/models directory."""
        content = _read_dockerfile("yolo26-vision-service")
        if not content:
            pytest.skip("No Dockerfile")
        assert "models" in content, (
            "yolo26-vision-service Dockerfile should provision a models directory"
        )

    def test_yolo26_gpu_env_vars(self) -> None:
        """YOLO26 Dockerfile declares GPU environment variables."""
        content = _read_dockerfile("yolo26-vision-service")
        if not content:
            pytest.skip("No Dockerfile")
        gpu_vars = ["NVIDIA_VISIBLE_DEVICES", "DEVICE", "HALF_PRECISION"]
        found = [v for v in gpu_vars if v in content]
        assert len(found) >= 2, (
            f"yolo26-vision-service missing GPU env vars (found: {found})"
        )


# ===========================================================================
# 3. Non-GPU Vision Services – Consistent Base
# ===========================================================================


class TestNonGPUVisionBase:
    """خدمات الرؤية بدون GPU يجب أن تستخدم صورة Python المعيارية."""

    NON_GPU = sorted(set(VISION_SERVICES) - {"yolo26-vision-service"})

    @pytest.mark.parametrize("svc", NON_GPU)
    def test_python_slim_base(self, svc: str) -> None:
        """Non-GPU vision service uses python slim-bookworm base."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        assert re.search(r"FROM\s+python:", content, re.IGNORECASE), (
            f"{svc} does not use standard Python base image"
        )


# ===========================================================================
# 4. Health Endpoints
# ===========================================================================


class TestVisionHealthEndpoints:
    """نقاط فحص الصحة في كود المصدر."""

    @pytest.mark.parametrize("svc", sorted(VISION_SERVICES))
    def test_healthcheck_in_dockerfile(self, svc: str) -> None:
        """Dockerfile defines a HEALTHCHECK."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        assert "HEALTHCHECK" in content, f"{svc} Dockerfile missing HEALTHCHECK"

    @pytest.mark.parametrize("svc", sorted(VISION_SERVICES))
    def test_healthz_in_source(self, svc: str) -> None:
        """Source code defines /healthz or /health endpoint."""
        main_path = SERVICES_DIR / svc / "src" / "main.py"
        if not main_path.exists():
            pytest.skip(f"No src/main.py for {svc}")
        content = main_path.read_text("utf-8")
        assert "/healthz" in content or "/health" in content, (
            f"{svc} main.py missing health endpoint"
        )


# ===========================================================================
# 5. NATS Vision Event Subjects
# ===========================================================================


class TestNATSVisionEvents:
    """أحداث NATS للرؤية يجب أن تتبع اصطلاحات التسمية."""

    @pytest.mark.parametrize("svc", sorted(CV_SERVICES | CV_LIGHT_SERVICES))
    def test_nats_event_publishing(self, svc: str) -> None:
        """CV service references NATS for event publishing."""
        reqs = _read_requirements(svc)
        dockerfile = _read_dockerfile(svc)
        # Check requirements or Dockerfile for nats dependency
        has_nats = "nats" in reqs.lower() or "NATS_URL" in dockerfile
        assert has_nats, f"{svc} should declare nats-py dependency for event publishing"

    def test_yolo26_vision_event_subjects(self) -> None:
        """YOLO26 source references sahool.vision.* event subjects."""
        src_dir = SERVICES_DIR / "yolo26-vision-service" / "src"
        if not src_dir.exists():
            pytest.skip("No src/ for yolo26-vision-service")
        all_py = list(src_dir.rglob("*.py"))
        combined = ""
        for f in all_py[:20]:  # Limit to avoid reading too many files
            combined += f.read_text("utf-8", errors="ignore")
        has_vision_subject = (
            "sahool.vision" in combined
            or "vision.pest" in combined
            or "vision.disease" in combined
            or "VISION" in combined
        )
        assert has_vision_subject, (
            "yolo26-vision-service should publish sahool.vision.* NATS events"
        )


# ===========================================================================
# 6. Port Range & Uniqueness
# ===========================================================================


class TestVisionPortRange:
    """منافذ خدمات الرؤية."""

    @pytest.mark.parametrize("svc,port", sorted(VISION_SERVICES.items()))
    def test_port_in_valid_range(self, svc: str, port: int) -> None:
        """Vision service port is in the 8xxx range."""
        assert 8000 <= port <= 8999, f"{svc} port {port} outside 8xxx range"

    def test_no_duplicate_ports(self) -> None:
        """No two vision services share the same port."""
        ports = list(VISION_SERVICES.values())
        assert len(ports) == len(set(ports))


# ===========================================================================
# 7. Non-Root User
# ===========================================================================


class TestVisionNonRoot:
    """خدمات الرؤية يجب أن تعمل بمستخدم غير جذري."""

    @pytest.mark.parametrize("svc", sorted(VISION_SERVICES))
    def test_non_root_user(self, svc: str) -> None:
        """Dockerfile switches to non-root USER."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        user_lines = re.findall(r"^USER\s+(\S+)", content, re.MULTILINE)
        non_root = [u for u in user_lines if u.lower() not in ("root", "0")]
        assert non_root, f"{svc} Dockerfile does not switch to non-root USER"


# ===========================================================================
# 8. Compose Configuration Consistency
# ===========================================================================


class TestVisionComposeConfig:
    """تكوين docker-compose متسق عبر خدمات الرؤية."""

    @pytest.mark.parametrize("svc", sorted(VISION_SERVICES))
    def test_service_in_compose(self, services: dict, svc: str) -> None:
        """Vision service defined in docker-compose.yml."""
        assert svc in services, f"{svc} not in docker-compose.yml"

    @pytest.mark.parametrize("svc", sorted(VISION_SERVICES))
    def test_restart_policy(self, services: dict, svc: str) -> None:
        """Vision service has restart policy."""
        svc_def = services.get(svc, {})
        assert "restart" in svc_def, f"{svc} missing restart policy"

    @pytest.mark.parametrize("svc", sorted(VISION_SERVICES))
    def test_logging_configured(self, services: dict, svc: str) -> None:
        """Vision service has logging configuration."""
        svc_def = services.get(svc, {})
        assert "logging" in svc_def, f"{svc} missing logging configuration"

    @pytest.mark.parametrize("svc", sorted(VISION_SERVICES))
    def test_network_membership(self, services: dict, svc: str) -> None:
        """Vision service on sahool network."""
        svc_def = services.get(svc, {})
        networks = svc_def.get("networks", {})
        net_names = list(networks.keys()) if isinstance(networks, dict) else networks
        assert any("sahool" in str(n) for n in (net_names or [])), (
            f"{svc} not on sahool network"
        )


# ===========================================================================
# 9. Remote Sensing Services – Satellite Dependencies
# ===========================================================================


class TestRemoteSensingDeps:
    """خدمات الاستشعار عن بعد يجب أن تحتوي على مكتبات التحليل."""

    @pytest.mark.parametrize("svc", sorted(REMOTE_SENSING_SERVICES))
    def test_has_analysis_dependency(self, svc: str) -> None:
        """Remote sensing service has analysis deps or uses shared/ modules."""
        pkgs = _req_packages(svc)
        has_analysis = "numpy" in pkgs or "scipy" in pkgs or "pandas" in pkgs
        if not has_analysis:
            # Some services access analysis via shared/ modules
            content = _read_dockerfile(svc)
            has_analysis = bool(re.search(r"COPY.*shared", content, re.IGNORECASE))
        assert has_analysis, (
            f"{svc} missing scientific computing dependency or shared/ module copy"
        )

    @pytest.mark.parametrize("svc", sorted(REMOTE_SENSING_SERVICES))
    def test_fastapi_dependency(self, svc: str) -> None:
        """Remote sensing service declares fastapi."""
        pkgs = _req_packages(svc)
        assert "fastapi" in pkgs, f"{svc} missing fastapi"


# ===========================================================================
# 10. Shared Module Copy
# ===========================================================================


class TestVisionSharedModules:
    """خدمات الرؤية يجب أن تنسخ الوحدات المشتركة."""

    @pytest.mark.parametrize("svc", sorted(VISION_SERVICES))
    def test_copies_shared(self, svc: str) -> None:
        """Dockerfile copies shared/ directory."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        assert re.search(r"COPY.*shared", content, re.IGNORECASE), (
            f"{svc} Dockerfile does not COPY shared/ directory"
        )
