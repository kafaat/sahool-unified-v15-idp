"""Regressions for the PyJWT dependency used by apps/services/shared/auth.

These tests load the affected source package in an isolated test namespace.
The similarly named root ``shared.auth`` package is a separate consumer and
cannot stand in for it.
"""

from __future__ import annotations

import base64
import importlib.util
import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import ModuleType

import jwt
import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name
from packaging.version import Version

pytestmark = [pytest.mark.unit, pytest.mark.security]

REPO_ROOT = Path(__file__).resolve().parents[3]
MANIFESTS = (
    REPO_ROOT / "apps/services/shared/requirements.txt",
    REPO_ROOT / "apps/services/shared/auth/requirements.txt",
)
MINIMUM_SECURE_VERSION = Version("2.15.1")


def _pyjwt_pin(path: Path) -> Version:
    """Require one unconditional, exact PyJWT pin in each independent manifest."""
    requirements = []
    for line in path.read_text(encoding="utf-8").splitlines():
        requirement = line.partition("#")[0].strip()
        if not requirement or requirement.startswith("-"):
            continue
        parsed = Requirement(requirement)
        if canonicalize_name(parsed.name) == "pyjwt":
            requirements.append(parsed)

    assert len(requirements) == 1, f"{path}: expected exactly one PyJWT requirement"
    requirement = requirements[0]
    assert requirement.marker is None, f"{path}: PyJWT must be pinned for every supported Python version"
    assert requirement.url is None, f"{path}: PyJWT must use a version pin"
    specifiers = list(requirement.specifier)
    assert len(specifiers) == 1, f"{path}: PyJWT must have one exact version pin"
    pin = specifiers[0]
    assert pin.operator == "==" and "*" not in pin.version, f"{path}: PyJWT must use == without a wildcard"
    version = Version(pin.version)
    assert not version.is_prerelease and not version.is_devrelease, f"{path}: PyJWT must use a stable release"
    assert MINIMUM_SECURE_VERSION <= version < Version("3"), f"{path}: PyJWT is outside the reviewed secure 2.x range"
    return version


def _matching_pyjwt_pin(paths: tuple[Path, Path]) -> Version:
    pins = [_pyjwt_pin(path) for path in paths]
    assert pins[0] == pins[1], f"Shared/auth PyJWT pins differ: {pins[0]} != {pins[1]}"
    return pins[0]


def test_shared_manifests_pin_the_same_secure_pyjwt_version():
    """Both installation entry points must stay on the same reviewed release."""
    _matching_pyjwt_pin(MANIFESTS)


@pytest.mark.parametrize(
    ("shared", "auth"),
    [
        ("PyJWT==2.15.1", "PyJWT==2.16.0"),
        ("PyJWT==2.11.0", "PyJWT==2.11.0"),
        ("PyJWT==2.15.1", "PyJWT>=2.15.1,<3"),
        ("PyJWT==2.15.1", "PyJWT==2.15.*"),
        ("PyJWT==2.15.1", "PyJWT==2.16.0rc1"),
        ("PyJWT==2.15.1", "PyJWT==2.15.1; python_version >= '3.12'"),
        ("PyJWT==2.15.1", "PyJWT==2.15.1\nPyJWT==2.15.1"),
        ("PyJWT==2.15.1", "# PyJWT pin was removed"),
    ],
    ids=["drift", "both-vulnerable", "range", "wildcard", "prerelease", "conditional", "duplicate", "missing"],
)
def test_pin_guard_rejects_drift_and_unsafe_declarations(tmp_path, shared, auth):
    paths = (tmp_path / "shared.txt", tmp_path / "auth.txt")
    for path, text in zip(paths, (shared, auth), strict=True):
        path.write_text(text + "\n", encoding="utf-8")
    with pytest.raises(AssertionError):
        _matching_pyjwt_pin(paths)


def test_pin_guard_accepts_normalized_names_extras_and_comments(tmp_path):
    paths = (tmp_path / "shared.txt", tmp_path / "auth.txt")
    paths[0].write_text("# JWT dependency\nPyJWT[crypto] == 2.15.1 # reviewed\n", encoding="utf-8")
    paths[1].write_text("pyjwt==2.15.1\n", encoding="utf-8")
    assert _matching_pyjwt_pin(paths) == MINIMUM_SECURE_VERSION


@pytest.fixture(scope="module")
def auth_package():
    """Load real auth code without touching another suite's apps namespace.

    tests/unit/services/conftest.py creates an apps package with an empty path.
    A private package name preserves the auth module's relative imports and
    keeps these tests independent of that collection-order side effect.
    """
    namespace = "_sahool_pyjwt_security_auth"
    assert not any(name == namespace or name.startswith(namespace + ".") for name in sys.modules)
    package_dir = REPO_ROOT / "apps/services/shared/auth"
    spec = importlib.util.spec_from_file_location(
        namespace,
        package_dir / "__init__.py",
        submodule_search_locations=[str(package_dir)],
    )
    assert spec is not None and spec.loader is not None
    package = importlib.util.module_from_spec(spec)
    sys.modules[namespace] = package
    try:
        spec.loader.exec_module(package)
        assert Path(package.jwt.__file__).resolve() == package_dir / "jwt.py"
        yield package
    finally:
        for name in tuple(sys.modules):
            if name == namespace or name.startswith(namespace + "."):
                del sys.modules[name]


@pytest.fixture
def config(auth_package, monkeypatch):
    auth_config = auth_package.config
    configuration = auth_config.AuthConfig(
        secret_key="shared-auth-security-test-key-with-at-least-64-bytes-for-hs512-testing",
        issuer="sahool-auth",
        audience="sahool-api",
    )
    monkeypatch.setattr(auth_config, "_config", configuration)
    return configuration


@pytest.fixture
def shared_jwt(auth_package, config):
    return auth_package.jwt


@pytest.fixture
def payload(config):
    now = int(datetime.now(UTC).timestamp())
    return {
        "sub": "farmer-123",
        "tenant_id": "tenant-456",
        "email": "farmer@example.test",
        "roles": ["viewer"],
        "permissions": ["field:read"],
        "type": "access",
        "jti": "shared-security-regression-jti",
        "iss": config.issuer,
        "aud": config.audience,
        "iat": now - 1,
        "exp": now + 300,
    }


@pytest.fixture
def client(auth_package, config):
    app = FastAPI()

    @app.get("/protected")
    async def protected(user=Depends(auth_package.get_current_user)):
        return {"id": user.id, "tenant_id": user.tenant_id, "roles": user.role_names}

    with TestClient(app) as test_client:
        yield test_client


def _assert_rejected_by_shared_auth(
    token: str, client: TestClient, shared_jwt: ModuleType, match: str = "Invalid token"
) -> None:
    with pytest.raises(ValueError, match=match):
        shared_jwt.decode_token(token)
    assert shared_jwt.verify_token(token) is False
    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_access_token_issuance_reaches_real_fastapi_consumer(shared_jwt, client):
    token, jti = shared_jwt.create_access_token(
        user_id="farmer-123",
        email="farmer@example.test",
        tenant_id="tenant-456",
        roles=["viewer"],
        permissions=["field:read"],
    )
    decoded = shared_jwt.decode_token(token)
    assert decoded.user_id == "farmer-123"
    assert decoded.tenant_id == "tenant-456"
    assert decoded.roles == ["viewer"]
    assert decoded.permissions == ["field:read"]
    assert decoded.jti == jti
    assert decoded.token_type == "access"
    assert decoded.exp > decoded.iat
    assert shared_jwt.verify_token(token)
    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {"id": "farmer-123", "tenant_id": "tenant-456", "roles": ["viewer"]}


def test_refresh_token_issuance_and_exchange(shared_jwt):
    token, jti, family_id = shared_jwt.create_refresh_token("farmer-123", tenant_id="tenant-456")
    decoded = shared_jwt.decode_token(token)
    assert decoded.user_id == "farmer-123"
    assert decoded.tenant_id == "tenant-456"
    assert decoded.jti == jti
    assert decoded.family_id == family_id
    assert decoded.token_type == "refresh"
    assert shared_jwt.verify_token(token, token_type="refresh")
    assert not shared_jwt.verify_token(token, token_type="access")

    access_token, access_jti = shared_jwt.refresh_access_token(token)
    assert access_jti != jti
    access_data = shared_jwt.decode_token(access_token)
    assert access_data.user_id == decoded.user_id
    assert access_data.tenant_id == decoded.tenant_id
    assert access_data.token_type == "access"
    assert shared_jwt.verify_token(access_token)


def test_access_token_cannot_be_exchanged_as_refresh(shared_jwt):
    token, _ = shared_jwt.create_access_token("farmer-123")
    with pytest.raises(ValueError, match="Expected refresh token"):
        shared_jwt.refresh_access_token(token)


def test_expired_token_is_rejected(shared_jwt, client):
    token, _ = shared_jwt.create_access_token("farmer-123", expires_delta=timedelta(seconds=-60))
    _assert_rejected_by_shared_auth(token, client, shared_jwt, match="Token has expired")


def test_wrong_signing_key_is_rejected(shared_jwt, payload, client):
    token = jwt.encode(payload, "different-test-signing-key-at-least-32-bytes", algorithm="HS256")
    _assert_rejected_by_shared_auth(token, client, shared_jwt)


def test_tampered_payload_is_rejected(config, shared_jwt, payload, client):
    token = jwt.encode(payload, config.secret_key, algorithm="HS256")
    header, _, signature = token.split(".")
    payload["sub"] = "different-user"
    altered_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b"=").decode()
    _assert_rejected_by_shared_auth(f"{header}.{altered_payload}.{signature}", client, shared_jwt)


@pytest.mark.parametrize("claim", ["exp", "iat", "sub", "iss", "aud"])
def test_missing_required_claim_is_rejected(config, shared_jwt, payload, client, claim):
    del payload[claim]
    token = jwt.encode(payload, config.secret_key, algorithm="HS256")
    _assert_rejected_by_shared_auth(token, client, shared_jwt)


@pytest.mark.parametrize(("claim", "value"), [("iss", "other-issuer"), ("aud", "other-audience")])
def test_wrong_issuer_or_audience_is_rejected(config, shared_jwt, payload, client, claim, value):
    payload[claim] = value
    token = jwt.encode(payload, config.secret_key, algorithm="HS256")
    _assert_rejected_by_shared_auth(token, client, shared_jwt)


@pytest.mark.parametrize("claim", ["iat", "nbf"])
def test_future_time_claim_is_rejected(config, shared_jwt, payload, client, claim):
    payload[claim] = int(datetime.now(UTC).timestamp()) + 300
    token = jwt.encode(payload, config.secret_key, algorithm="HS256")
    _assert_rejected_by_shared_auth(token, client, shared_jwt)


@pytest.mark.parametrize(("claim", "value"), [("exp", None), ("iat", []), ("nbf", {})])
def test_malformed_numeric_claim_produces_auth_error(config, shared_jwt, payload, client, claim, value):
    """New PyJWT releases normalize malformed NumericDate errors for callers."""
    payload[claim] = value
    token = jwt.encode(payload, config.secret_key, algorithm="HS256")
    _assert_rejected_by_shared_auth(token, client, shared_jwt)


@pytest.mark.parametrize("algorithm", ["HS384", "HS512", "none"])
def test_unconfigured_algorithm_is_rejected(config, shared_jwt, payload, client, algorithm):
    key = None if algorithm == "none" else config.secret_key
    token = jwt.encode(payload, key, algorithm=algorithm)
    _assert_rejected_by_shared_auth(token, client, shared_jwt)


@pytest.mark.parametrize("token", ["", "not-a-jwt", "bad.payload.signature", "a.b.c.d"])
def test_malformed_token_is_rejected(shared_jwt, client, token):
    _assert_rejected_by_shared_auth(token, client, shared_jwt)


def test_unknown_critical_extension_is_rejected(config, shared_jwt, payload, client):
    """CVE-2026-32597: correctly signed unsupported crit must fail closed."""
    # A valid control proves that signature, issuer, audience and claims match.
    valid = jwt.encode(payload, config.secret_key, algorithm="HS256")
    assert shared_jwt.decode_token(valid).user_id == payload["sub"]
    token = jwt.encode(
        payload,
        config.secret_key,
        algorithm="HS256",
        headers={"crit": ["x-sahool-required-policy"], "x-sahool-required-policy": "test-policy"},
    )
    _assert_rejected_by_shared_auth(token, client, shared_jwt, match="Unsupported critical extension")


def test_noncritical_extension_remains_compatible(config, shared_jwt, payload, client):
    token = jwt.encode(
        payload,
        config.secret_key,
        algorithm="HS256",
        headers={"x-sahool-metadata": "test-value"},
    )
    assert shared_jwt.decode_token(token).user_id == payload["sub"]
    assert shared_jwt.verify_token(token)
    assert client.get("/protected", headers={"Authorization": f"Bearer {token}"}).status_code == 200


def test_padded_signature_remains_compatible(config, shared_jwt, payload):
    """2.15.1 retains acceptance of trailing Base64URL signature padding."""
    token = jwt.encode(payload, config.secret_key, algorithm="HS256")
    header, body, signature = token.split(".")
    padded_signature = signature + "=" * (-len(signature) % 4)
    assert padded_signature != signature
    assert shared_jwt.decode_token(f"{header}.{body}.{padded_signature}").user_id == payload["sub"]


def test_absent_bearer_token_is_rejected(config, client):
    response = client.get("/protected")
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
