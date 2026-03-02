"""
SAHOOL vLLM Container & Infrastructure Tests
==============================================
اختبارات حاوية و بنية تحتية vLLM

Comprehensive tests validating:
1. Dockerfile correctness (base image, security, health checks)
2. docker-compose.vllm.yml structure (GPU, volumes, networks)
3. docker-compose.yml vLLM service integration
4. Governance service registry entry
5. Kong API gateway route configuration
6. Prometheus monitoring scrape config
7. .env.example variables
8. Makefile targets
9. Constraints file entry
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

pytestmark = [pytest.mark.container]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
VLLM_DIR = REPO_ROOT / "infrastructure" / "core" / "vllm"
MAIN_COMPOSE = REPO_ROOT / "docker-compose.yml"
VLLM_COMPOSE = VLLM_DIR / "docker-compose.vllm.yml"
VLLM_DOCKERFILE = VLLM_DIR / "Dockerfile"
VLLM_ENV_EXAMPLE = VLLM_DIR / ".env.example"
VLLM_README = VLLM_DIR / "README.md"
KONG_YML = REPO_ROOT / "infrastructure" / "gateway" / "kong" / "kong.yml"
PROMETHEUS_YML = REPO_ROOT / "infrastructure" / "monitoring" / "prometheus" / "prometheus.yml"
GOVERNANCE_SERVICES = REPO_ROOT / "governance" / "services.yaml"
MAKEFILE = REPO_ROOT / "Makefile"
ENV_EXAMPLE = REPO_ROOT / ".env.example"
CONSTRAINTS_AI = REPO_ROOT / "docker" / "constraints-ai.txt"


def _load_yaml(path: Path) -> dict:
    """Load and parse a YAML file."""
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _read_text(path: Path) -> str:
    """Read file as text."""
    return path.read_text(encoding="utf-8")


# ═══════════════════════════════════════════════════════════════════════════
# File Existence Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestVLLMFileStructure:
    """Test that all vLLM infrastructure files exist."""

    def test_dockerfile_exists(self):
        """vLLM Dockerfile exists."""
        assert VLLM_DOCKERFILE.exists(), f"Missing: {VLLM_DOCKERFILE}"

    def test_compose_file_exists(self):
        """vLLM docker-compose.vllm.yml exists."""
        assert VLLM_COMPOSE.exists(), f"Missing: {VLLM_COMPOSE}"

    def test_env_example_exists(self):
        """vLLM .env.example exists."""
        assert VLLM_ENV_EXAMPLE.exists(), f"Missing: {VLLM_ENV_EXAMPLE}"

    def test_readme_exists(self):
        """vLLM README.md exists."""
        assert VLLM_README.exists(), f"Missing: {VLLM_README}"

    def test_vllm_directory_structure(self):
        """vLLM directory has all expected files."""
        expected_files = ["Dockerfile", "docker-compose.vllm.yml", ".env.example", "README.md"]
        for fname in expected_files:
            fpath = VLLM_DIR / fname
            assert fpath.exists(), f"Missing {fname} in {VLLM_DIR}"


# ═══════════════════════════════════════════════════════════════════════════
# Dockerfile Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestVLLMDockerfile:
    """Test vLLM Dockerfile follows best practices."""

    @pytest.fixture(autouse=True)
    def _load_dockerfile(self):
        self.content = _read_text(VLLM_DOCKERFILE)

    def test_uses_nvidia_cuda_base_image(self):
        """Dockerfile uses NVIDIA CUDA base image."""
        assert "nvidia/cuda" in self.content
        assert "cudnn8" in self.content

    def test_cuda_version_12_1(self):
        """Dockerfile uses CUDA 12.1."""
        assert "12.1.1" in self.content or "12.1" in self.content

    def test_ubuntu_base(self):
        """Dockerfile uses Ubuntu base."""
        assert "ubuntu" in self.content.lower()

    def test_non_root_user(self):
        """Dockerfile creates and uses non-root user 'sahool'."""
        assert "useradd" in self.content
        assert "sahool" in self.content
        assert "USER sahool" in self.content

    def test_uid_gid_1000(self):
        """Non-root user uses UID/GID 1000."""
        assert "--uid 1000" in self.content
        assert "--gid 1000" in self.content or "--gid sahool" in self.content

    def test_healthcheck_defined(self):
        """Dockerfile has HEALTHCHECK directive."""
        assert "HEALTHCHECK" in self.content

    def test_healthcheck_uses_health_endpoint(self):
        """HEALTHCHECK checks /health endpoint."""
        assert "/health" in self.content

    def test_healthcheck_start_period(self):
        """HEALTHCHECK has sufficient start period (model loading takes time)."""
        match = re.search(r"--start-period=(\d+)s", self.content)
        assert match, "Missing start-period in HEALTHCHECK"
        start_period = int(match.group(1))
        assert start_period >= 120, f"Start period {start_period}s too short for model loading"

    def test_expose_port(self):
        """Dockerfile EXPOSEs the vLLM port."""
        assert "EXPOSE" in self.content

    def test_python_311(self):
        """Dockerfile targets Python 3.11."""
        assert "3.11" in self.content

    def test_vllm_package_installed(self):
        """Dockerfile installs vllm package."""
        assert "vllm" in self.content

    def test_pip_no_cache_dir(self):
        """Dockerfile uses --no-cache-dir for pip."""
        assert "--no-cache-dir" in self.content or "PIP_NO_CACHE_DIR" in self.content

    def test_multi_mirror_pip_fallback(self):
        """Dockerfile uses multi-mirror pip fallback pattern."""
        assert "pypi.org" in self.content
        assert "mirrors.aliyun.com" in self.content or "mirrors.cloud.tencent.com" in self.content

    def test_oci_labels(self):
        """Dockerfile has OCI image labels."""
        assert "org.opencontainers.image" in self.content
        assert "KAFAAT" in self.content

    def test_cmd_runs_vllm_serve(self):
        """Dockerfile CMD runs vllm serve."""
        assert "vllm serve" in self.content

    def test_cmd_includes_trust_remote_code(self):
        """CMD includes --trust-remote-code flag."""
        assert "--trust-remote-code" in self.content

    def test_cmd_includes_gpu_memory_utilization(self):
        """CMD includes --gpu-memory-utilization setting."""
        assert "--gpu-memory-utilization" in self.content

    def test_env_vllm_model(self):
        """Dockerfile sets VLLM_MODEL environment variable."""
        assert "VLLM_MODEL" in self.content
        assert "deepseek-ai/deepseek-coder-6.7b-instruct" in self.content

    def test_env_vllm_port(self):
        """Dockerfile sets VLLM_PORT environment variable."""
        assert "VLLM_PORT" in self.content

    def test_env_vllm_max_model_len(self):
        """Dockerfile sets VLLM_MAX_MODEL_LEN environment variable."""
        assert "VLLM_MAX_MODEL_LEN" in self.content
        assert "16384" in self.content

    def test_env_nvidia_visible_devices(self):
        """Dockerfile sets NVIDIA_VISIBLE_DEVICES."""
        assert "NVIDIA_VISIBLE_DEVICES" in self.content

    def test_env_hf_home(self):
        """Dockerfile sets HF_HOME for HuggingFace cache."""
        assert "HF_HOME" in self.content

    def test_workdir_set(self):
        """Dockerfile sets WORKDIR."""
        assert "WORKDIR" in self.content

    def test_models_directory_created(self):
        """Dockerfile creates /models directory."""
        assert "/models" in self.content

    def test_no_root_runtime(self):
        """User switch happens before CMD, not running as root."""
        user_line = self.content.rfind("USER sahool")
        cmd_line = self.content.rfind("CMD")
        assert user_line < cmd_line, "USER sahool must come before CMD"


# ═══════════════════════════════════════════════════════════════════════════
# docker-compose.vllm.yml Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestVLLMComposeStandalone:
    """Test standalone vLLM docker-compose file."""

    @pytest.fixture(autouse=True)
    def _load_compose(self):
        self.compose = _load_yaml(VLLM_COMPOSE)

    def test_has_services_section(self):
        """Compose file has services section."""
        assert "services" in self.compose

    def test_vllm_service_defined(self):
        """vLLM service is defined."""
        assert "vllm" in self.compose["services"]

    def test_container_name(self):
        """Container is named sahool-vllm."""
        vllm = self.compose["services"]["vllm"]
        assert vllm.get("container_name") == "sahool-vllm"

    def test_image_tag(self):
        """Image uses sahool/vllm-deepseek:16.0.0 tag."""
        vllm = self.compose["services"]["vllm"]
        assert "sahool/vllm-deepseek" in vllm.get("image", "")

    def test_build_context_points_to_repo_root(self):
        """Build context points to repository root."""
        vllm = self.compose["services"]["vllm"]
        build = vllm.get("build", {})
        context = build.get("context", "")
        assert context == "../../../" or context == "../../.."

    def test_build_dockerfile_path(self):
        """Build uses correct Dockerfile path."""
        vllm = self.compose["services"]["vllm"]
        build = vllm.get("build", {})
        dockerfile = build.get("dockerfile", "")
        assert "infrastructure/core/vllm/Dockerfile" in dockerfile

    def test_gpu_reservation(self):
        """Service has NVIDIA GPU reservation."""
        vllm = self.compose["services"]["vllm"]
        deploy = vllm.get("deploy", {})
        resources = deploy.get("resources", {})
        reservations = resources.get("reservations", {})
        devices = reservations.get("devices", [])

        assert len(devices) >= 1
        gpu_device = devices[0]
        assert gpu_device.get("driver") == "nvidia"
        assert "gpu" in gpu_device.get("capabilities", [[]])[0]

    def test_volumes_defined(self):
        """Service has persistent volumes for models and HF cache."""
        vllm = self.compose["services"]["vllm"]
        volumes = vllm.get("volumes", [])
        volume_strs = [str(v) for v in volumes]

        has_models = any("/models" in v for v in volume_strs)
        has_hf_cache = any("huggingface" in v for v in volume_strs)

        assert has_models, "Missing /models volume mount"
        assert has_hf_cache, "Missing HuggingFace cache volume mount"

    def test_named_volumes_created(self):
        """Top-level volumes section defines named volumes."""
        volumes = self.compose.get("volumes", {})
        volume_names = list(volumes.keys())
        assert any("vllm" in v for v in volume_names), f"No vllm volumes found: {volume_names}"

    def test_environment_variables(self):
        """Service has required environment variables."""
        vllm = self.compose["services"]["vllm"]
        env = vllm.get("environment", [])
        env_str = str(env)

        assert "VLLM_MODEL" in env_str
        assert "VLLM_PORT" in env_str
        assert "NVIDIA_VISIBLE_DEVICES" in env_str

    def test_healthcheck_defined(self):
        """Service has healthcheck configured."""
        vllm = self.compose["services"]["vllm"]
        healthcheck = vllm.get("healthcheck")
        assert healthcheck is not None

    def test_healthcheck_test_command(self):
        """Healthcheck test uses curl to /health."""
        vllm = self.compose["services"]["vllm"]
        healthcheck = vllm.get("healthcheck", {})
        test = healthcheck.get("test", [])
        test_str = str(test)
        assert "curl" in test_str
        assert "/health" in test_str

    def test_restart_policy(self):
        """Service has restart policy set."""
        vllm = self.compose["services"]["vllm"]
        assert vllm.get("restart") == "unless-stopped"

    def test_network_sahool(self):
        """Service connects to sahool-network."""
        vllm = self.compose["services"]["vllm"]
        networks = vllm.get("networks", [])
        assert "sahool-network" in networks

    def test_external_network(self):
        """sahool-network is declared external."""
        networks = self.compose.get("networks", {})
        sahool_net = networks.get("sahool-network", {})
        assert sahool_net.get("external") is True

    def test_logging_configured(self):
        """Service has logging configuration."""
        vllm = self.compose["services"]["vllm"]
        logging = vllm.get("logging")
        assert logging is not None
        assert logging.get("driver") == "json-file"

    def test_port_binding_localhost_only(self):
        """Port binding restricts to localhost (127.0.0.1)."""
        vllm = self.compose["services"]["vllm"]
        ports = vllm.get("ports", [])
        port_str = str(ports)
        assert "127.0.0.1" in port_str, "Port should bind to localhost only"


# ═══════════════════════════════════════════════════════════════════════════
# Main docker-compose.yml Integration Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestVLLMMainComposeIntegration:
    """Test vLLM service in main docker-compose.yml."""

    @pytest.fixture(autouse=True)
    def _load_compose(self):
        self.compose = _load_yaml(MAIN_COMPOSE)

    def test_vllm_service_in_main_compose(self):
        """vLLM service exists in main docker-compose.yml."""
        assert "vllm" in self.compose.get("services", {}), "vLLM service missing from main compose"

    def test_vllm_under_gpu_profile(self):
        """vLLM service is under 'gpu' profile."""
        vllm = self.compose["services"]["vllm"]
        profiles = vllm.get("profiles", [])
        assert "gpu" in profiles, f"Expected 'gpu' profile, got {profiles}"

    def test_vllm_has_gpu_reservation_in_main(self):
        """vLLM in main compose has GPU device reservation."""
        vllm = self.compose["services"]["vllm"]
        deploy = vllm.get("deploy", {})
        resources = deploy.get("resources", {})
        reservations = resources.get("reservations", {})
        devices = reservations.get("devices", [])

        has_nvidia = any(d.get("driver") == "nvidia" for d in devices)
        assert has_nvidia, "Missing NVIDIA GPU reservation"

    def test_vllm_volumes_in_main_compose(self):
        """Main compose defines vLLM volumes."""
        volumes = self.compose.get("volumes", {})
        volume_names = list(volumes.keys())
        has_vllm_volume = any("vllm" in v for v in volume_names)
        assert has_vllm_volume, f"No vllm volumes in main compose: {volume_names}"


# ═══════════════════════════════════════════════════════════════════════════
# .env.example Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestVLLMEnvExample:
    """Test vLLM .env.example files."""

    def test_vllm_local_env_has_model(self):
        """Local .env.example has VLLM_MODEL."""
        content = _read_text(VLLM_ENV_EXAMPLE)
        assert "VLLM_MODEL" in content

    def test_vllm_local_env_has_port(self):
        """Local .env.example has VLLM_PORT."""
        content = _read_text(VLLM_ENV_EXAMPLE)
        assert "VLLM_PORT" in content

    def test_root_env_has_vllm_variables(self):
        """Root .env.example has VLLM configuration variables."""
        content = _read_text(ENV_EXAMPLE)
        assert "VLLM_MODEL" in content
        assert "VLLM_PORT" in content
        assert "VLLM_BASE_URL" in content

    def test_root_env_vllm_model_default(self):
        """Root .env.example sets correct default model."""
        content = _read_text(ENV_EXAMPLE)
        assert "deepseek-ai/deepseek-coder-6.7b-instruct" in content

    def test_root_env_vllm_gpu_count(self):
        """Root .env.example has VLLM_GPU_COUNT."""
        content = _read_text(ENV_EXAMPLE)
        assert "VLLM_GPU_COUNT" in content

    def test_root_env_vllm_memory_limit(self):
        """Root .env.example has VLLM_MEMORY_LIMIT."""
        content = _read_text(ENV_EXAMPLE)
        assert "VLLM_MEMORY_LIMIT" in content

    def test_no_secrets_in_env_example(self):
        """No actual secrets/tokens in .env.example files."""
        for env_file in [VLLM_ENV_EXAMPLE, ENV_EXAMPLE]:
            content = _read_text(env_file)
            lines = content.splitlines()
            for line in lines:
                if "HF_TOKEN" in line and "=" in line:
                    value = line.split("=", 1)[1].strip()
                    assert value == "" or value.startswith("${"), (
                        f"HF_TOKEN should be empty in {env_file.name}"
                    )


# ═══════════════════════════════════════════════════════════════════════════
# Governance Service Registry Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestVLLMGovernanceRegistry:
    """Test vLLM entry in governance/services.yaml."""

    @pytest.fixture(autouse=True)
    def _load_governance(self):
        self.services = _load_yaml(GOVERNANCE_SERVICES)

    def test_vllm_deepseek_in_registry(self):
        """vllm-deepseek is registered in services.yaml."""
        service_list = self.services.get("services", {})
        assert "vllm-deepseek" in service_list, "vllm-deepseek not found in service registry"

    def test_vllm_in_intelligence_layer(self):
        """vllm-deepseek is in the intelligence layer."""
        event_arch = self.services.get("event_architecture", {})
        layers = event_arch.get("layers", {})
        intelligence = layers.get("intelligence", {})
        services = intelligence.get("services", [])
        assert "vllm-deepseek" in services, "vllm-deepseek not in intelligence layer"

    def test_vllm_service_port(self):
        """vllm-deepseek has port 8270."""
        service = self.services["services"]["vllm-deepseek"]
        assert service.get("port") == 8270

    def test_vllm_service_type(self):
        """vllm-deepseek is type python."""
        service = self.services["services"]["vllm-deepseek"]
        assert service.get("type") == "python"

    def test_vllm_service_has_health_endpoint(self):
        """vllm-deepseek has /health endpoint defined."""
        service = self.services["services"]["vllm-deepseek"]
        assert service.get("health_endpoint") == "/health"

    def test_vllm_service_has_name(self):
        """vllm-deepseek has human-readable name."""
        service = self.services["services"]["vllm-deepseek"]
        assert "name" in service
        assert "vLLM" in service["name"]

    def test_vllm_service_has_arabic_name(self):
        """vllm-deepseek has Arabic name."""
        service = self.services["services"]["vllm-deepseek"]
        assert "name_ar" in service


# ═══════════════════════════════════════════════════════════════════════════
# Kong API Gateway Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestVLLMKongGateway:
    """Test vLLM route configuration in Kong."""

    @pytest.fixture(autouse=True)
    def _load_kong(self):
        self.kong = _load_yaml(KONG_YML)

    def test_vllm_service_in_kong(self):
        """vLLM service is registered in Kong."""
        services = self.kong.get("services", [])
        vllm_services = [s for s in services if "vllm" in s.get("name", "")]
        assert len(vllm_services) >= 1, "No vLLM service in Kong config"

    def test_vllm_service_host(self):
        """Kong vLLM service points to correct host."""
        services = self.kong.get("services", [])
        vllm_svc = next(s for s in services if "vllm" in s.get("name", ""))
        assert vllm_svc.get("host") == "vllm"

    def test_vllm_service_port_8270(self):
        """Kong vLLM service uses port 8270."""
        services = self.kong.get("services", [])
        vllm_svc = next(s for s in services if "vllm" in s.get("name", ""))
        assert vllm_svc.get("port") == 8270

    def test_vllm_route_paths(self):
        """Kong has route paths for vLLM."""
        services = self.kong.get("services", [])
        vllm_svc = next(s for s in services if "vllm" in s.get("name", ""))
        routes = vllm_svc.get("routes", [])
        assert len(routes) >= 1, "No routes defined for vLLM"

        all_paths = []
        for route in routes:
            all_paths.extend(route.get("paths", []))
        path_str = str(all_paths)
        assert "vllm" in path_str, f"No /vllm path found in {all_paths}"

    def test_vllm_long_timeouts(self):
        """Kong vLLM service has long timeouts for inference."""
        services = self.kong.get("services", [])
        vllm_svc = next(s for s in services if "vllm" in s.get("name", ""))

        read_timeout = vllm_svc.get("read_timeout", 0)
        write_timeout = vllm_svc.get("write_timeout", 0)

        assert read_timeout >= 60000, f"Read timeout {read_timeout}ms too short"
        assert write_timeout >= 60000, f"Write timeout {write_timeout}ms too short"


# ═══════════════════════════════════════════════════════════════════════════
# Prometheus Monitoring Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestVLLMPrometheusMonitoring:
    """Test vLLM scrape configuration in Prometheus."""

    @pytest.fixture(autouse=True)
    def _load_prometheus(self):
        self.prom = _load_yaml(PROMETHEUS_YML)

    def test_vllm_scrape_job_exists(self):
        """Prometheus has a scrape job for vLLM."""
        scrape_configs = self.prom.get("scrape_configs", [])
        job_names = [j.get("job_name") for j in scrape_configs]
        assert any("vllm" in name for name in job_names if name), (
            f"No vLLM scrape job found. Jobs: {job_names}"
        )

    def test_vllm_scrape_target(self):
        """Prometheus scrapes vllm:8270."""
        scrape_configs = self.prom.get("scrape_configs", [])
        vllm_job = next(
            (j for j in scrape_configs if "vllm" in j.get("job_name", "")),
            None,
        )
        assert vllm_job is not None

        static_configs = vllm_job.get("static_configs", [])
        all_targets = []
        for sc in static_configs:
            all_targets.extend(sc.get("targets", []))
        assert any("vllm:8270" in t for t in all_targets), (
            f"vllm:8270 not in targets: {all_targets}"
        )

    def test_vllm_scrape_labels(self):
        """Prometheus vLLM job has ai-ml tier label."""
        scrape_configs = self.prom.get("scrape_configs", [])
        vllm_job = next(
            (j for j in scrape_configs if "vllm" in j.get("job_name", "")),
            None,
        )
        assert vllm_job is not None

        static_configs = vllm_job.get("static_configs", [])
        for sc in static_configs:
            labels = sc.get("labels", {})
            if labels.get("service") and "vllm" in labels["service"]:
                assert labels.get("tier") == "ai-ml"
                break


# ═══════════════════════════════════════════════════════════════════════════
# Makefile Targets Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestVLLMMakefileTargets:
    """Test vLLM Makefile targets exist."""

    @pytest.fixture(autouse=True)
    def _load_makefile(self):
        self.makefile = _read_text(MAKEFILE)

    def test_dev_vllm_target(self):
        """Makefile has dev-vllm target."""
        assert "dev-vllm:" in self.makefile

    def test_build_vllm_target(self):
        """Makefile has build-vllm target."""
        assert "build-vllm:" in self.makefile

    def test_logs_vllm_target(self):
        """Makefile has logs-vllm target."""
        assert "logs-vllm:" in self.makefile

    def test_stop_vllm_target(self):
        """Makefile has stop-vllm target."""
        assert "stop-vllm:" in self.makefile

    def test_dev_vllm_uses_gpu_profile(self):
        """dev-vllm target uses --profile gpu."""
        assert "--profile gpu" in self.makefile

    def test_phony_targets_declared(self):
        """vLLM targets are declared in .PHONY."""
        # Find .PHONY lines
        phony_lines = [line for line in self.makefile.splitlines() if ".PHONY:" in line]
        phony_str = " ".join(phony_lines)
        assert "dev-vllm" in phony_str or "build-vllm" in phony_str


# ═══════════════════════════════════════════════════════════════════════════
# Constraints File Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestVLLMConstraints:
    """Test vLLM in constraints-ai.txt."""

    def test_vllm_constraint_exists(self):
        """vllm package is in constraints-ai.txt."""
        content = _read_text(CONSTRAINTS_AI)
        assert "vllm" in content

    def test_vllm_version_range(self):
        """vllm constraint specifies version range."""
        content = _read_text(CONSTRAINTS_AI)
        # Should have vllm>=0.6.0,<1.0.0 or similar
        vllm_lines = [line for line in content.splitlines() if line.strip().startswith("vllm")]
        assert len(vllm_lines) >= 1, "No vllm constraint line found"
        vllm_line = vllm_lines[0]
        assert ">=" in vllm_line, f"Missing lower bound in: {vllm_line}"
        assert "<" in vllm_line, f"Missing upper bound in: {vllm_line}"


# ═══════════════════════════════════════════════════════════════════════════
# README Documentation Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestVLLMReadme:
    """Test vLLM README.md documentation completeness."""

    @pytest.fixture(autouse=True)
    def _load_readme(self):
        self.readme = _read_text(VLLM_README)

    def test_readme_has_title(self):
        """README has a title."""
        assert "# " in self.readme

    def test_readme_mentions_deepseek(self):
        """README mentions DeepSeek model."""
        assert "deepseek" in self.readme.lower() or "DeepSeek" in self.readme

    def test_readme_has_api_usage(self):
        """README has API usage section."""
        assert "API" in self.readme

    def test_readme_has_quick_start(self):
        """README has quick start section."""
        assert "Quick Start" in self.readme or "بدء سريع" in self.readme

    def test_readme_has_environment_variables(self):
        """README documents environment variables."""
        assert "VLLM_MODEL" in self.readme

    def test_readme_has_gpu_requirements(self):
        """README documents GPU memory requirements."""
        assert "GPU" in self.readme
        assert "VRAM" in self.readme or "memory" in self.readme.lower()

    def test_readme_bilingual(self):
        """README has Arabic content."""
        # Check for Arabic characters
        has_arabic = bool(re.search(r"[\u0600-\u06FF]", self.readme))
        assert has_arabic, "README should be bilingual (English/Arabic)"

    def test_readme_has_health_check_endpoint(self):
        """README documents health check endpoint."""
        assert "/health" in self.readme

    def test_readme_has_chat_completions_endpoint(self):
        """README documents chat completions endpoint."""
        assert "/v1/chat/completions" in self.readme


# ═══════════════════════════════════════════════════════════════════════════
# Cross-Component Consistency Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestVLLMCrossComponentConsistency:
    """Test consistency across all vLLM configuration files."""

    def test_port_consistency(self):
        """Port 8270 is consistent across all config files."""
        dockerfile = _read_text(VLLM_DOCKERFILE)
        compose = _read_text(VLLM_COMPOSE)
        env = _read_text(VLLM_ENV_EXAMPLE)

        assert "8270" in dockerfile
        assert "8270" in compose
        assert "8270" in env

    def test_model_name_consistency(self):
        """Model name is consistent across configurations."""
        model = "deepseek-ai/deepseek-coder-6.7b-instruct"

        dockerfile = _read_text(VLLM_DOCKERFILE)
        compose = _read_text(VLLM_COMPOSE)
        env = _read_text(VLLM_ENV_EXAMPLE)
        readme = _read_text(VLLM_README)

        assert model in dockerfile
        assert model in compose
        assert model in env
        assert model in readme

    def test_container_name_consistency(self):
        """Container name sahool-vllm is consistent."""
        compose = _load_yaml(VLLM_COMPOSE)
        main_compose = _load_yaml(MAIN_COMPOSE)

        standalone_name = compose["services"]["vllm"].get("container_name")
        main_name = main_compose["services"]["vllm"].get("container_name")

        assert standalone_name == "sahool-vllm"
        assert main_name == "sahool-vllm"

    def test_max_model_len_consistency(self):
        """max-model-len 16384 is consistent across configurations."""
        dockerfile = _read_text(VLLM_DOCKERFILE)
        compose = _read_text(VLLM_COMPOSE)
        env = _read_text(VLLM_ENV_EXAMPLE)

        assert "16384" in dockerfile
        assert "16384" in compose
        assert "16384" in env

    def test_version_consistency(self):
        """Version 16.0.0 is consistent across configurations."""
        dockerfile = _read_text(VLLM_DOCKERFILE)
        compose = _read_text(VLLM_COMPOSE)

        assert "16.0.0" in dockerfile
        assert "16.0.0" in compose
