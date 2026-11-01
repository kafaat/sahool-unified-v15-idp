"""Exercise the parser, TLS and encryption contracts affected by dependency updates."""

from __future__ import annotations

import base64
import importlib.util
import io
import ssl
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import Mock

import anyio
import httpx
import pytest
from anyio.streams.stapled import StapledObjectStream
from anyio.streams.tls import TLSStream
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from fastapi import FastAPI, File, Form, Request, UploadFile
from pydantic import BaseModel, ValidationError
from pydantic_settings import BaseSettings, NestedSecretsSettingsSource, SettingsConfigDict, SettingsError
from python_multipart import MultipartParser, parse_form
from python_multipart.exceptions import MultipartParseError
from python_multipart.multipart import parse_options_header

pytestmark = [pytest.mark.unit, pytest.mark.security]


@pytest.fixture
def form_app():
    """Use the same FastAPI form/upload APIs as consuming services."""
    app = FastAPI()

    @app.post("/form")
    async def parse_fields(request: Request):
        return dict(await request.form())

    @app.post("/upload")
    async def upload(field_id: str = Form(...), file: UploadFile = File(...)):
        return {
            "field_id": field_id,
            "filename": file.filename,
            "content_type": file.content_type,
            "content": (await file.read()).decode(),
        }

    return app


@pytest.mark.asyncio
@pytest.mark.parametrize("split_at", [None, 1, 11, 12, 14])
async def test_form_semicolon_cannot_smuggle_an_overriding_field(form_app, split_at):
    """CVE-2026-53538/53539: only '&' separates fields, across chunk boundaries."""
    body = b"role=user&x=;role=admin"

    async def chunks():
        if split_at is None:
            yield body
        else:
            yield body[:split_at]
            yield body[split_at:]

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=form_app), base_url="http://test") as client:
        response = await client.post(
            "/form", content=chunks(), headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
    assert response.status_code == 200
    assert response.json() == {"role": "user", "x": ";role=admin"}


@pytest.mark.asyncio
async def test_regular_multipart_upload_preserves_unicode_and_file_data(form_app):
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=form_app), base_url="http://test") as client:
        response = await client.post(
            "/upload",
            data={"field_id": "حقل-123"},
            files={"file": ("crop.txt", "قمح\n".encode(), "text/plain")},
        )
    assert response.status_code == 200
    assert response.json() == {
        "field_id": "حقل-123",
        "filename": "crop.txt",
        "content_type": "text/plain",
        "content": "قمح\n",
    }


@pytest.mark.parametrize("chunk_size", [97, 131072])
@pytest.mark.parametrize(
    "headers",
    [b"X-Extra: a\r\n" * 32, b"X-Extra: " + b"a" * 65536 + b"\r\n"],
    ids=["too-many-headers", "oversized-header"],
)
def test_multipart_default_header_limits_reject_oversized_parts(headers, chunk_size):
    """CVE-2026-42561: limits must survive incremental request-body delivery."""
    body = b"--boundary\r\n" + headers + b"\r\nvalue\r\n--boundary--\r\n"
    parser = MultipartParser(b"boundary")
    with pytest.raises(MultipartParseError):
        for offset in range(0, len(body), chunk_size):
            parser.write(body[offset : offset + chunk_size])


def test_negative_content_length_is_rejected_before_reading_the_body():
    """CVE-2026-53540: a negative length must never become read(-1)."""
    stream = Mock(wraps=io.BytesIO(b"field=value"))
    with pytest.raises(ValueError, match="Content-Length.*non-negative"):
        parse_form(
            {"Content-Type": b"application/x-www-form-urlencoded", "Content-Length": b"-1"},
            stream,
            None,
            None,
        )
    stream.read.assert_not_called()


def test_extended_content_disposition_cannot_override_the_plain_field_name():
    """Keep the RFC 7578 field name authoritative at the upload boundary."""
    _, parameters = parse_options_header(b"form-data; name=\"field_id\"; name*=utf-8''role")
    assert parameters[b"name"] == b"field_id"


def _tls_contexts(tmp_path: Path, certificate_hostname: str):
    """Create a local, explicitly trusted certificate; no network or external CA."""
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "dependency-regression-test")])
    now = datetime.now(UTC)
    certificate = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=1))
        .not_valid_after(now + timedelta(days=1))
        .add_extension(x509.SubjectAlternativeName([x509.DNSName(certificate_hostname)]), critical=False)
        .sign(key, hashes.SHA256())
    )
    certificate_path = tmp_path / "server.pem"
    key_path = tmp_path / "server-key.pem"
    certificate_path.write_bytes(certificate.public_bytes(serialization.Encoding.PEM))
    key_path.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    server_context.load_cert_chain(certificate_path, key_path)
    client_context = ssl.create_default_context(cafile=str(certificate_path))
    assert client_context.check_hostname
    assert client_context.verify_mode == ssl.CERT_REQUIRED
    return server_context, client_context


@pytest.mark.asyncio
@pytest.mark.parametrize("certificate_hostname", ["xn--fa-hia.de", "fass.de"])
async def test_anyio_tls_uses_idna2008_for_certificate_validation(tmp_path, certificate_hostname):
    """CVE-2026-63374: faß.de must never authenticate a certificate for fass.de."""
    server_context, client_context = _tls_contexts(tmp_path, certificate_hostname)
    server_send, server_receive = anyio.create_memory_object_stream[bytes](8)
    client_send, client_receive = anyio.create_memory_object_stream[bytes](8)
    client_stream = StapledObjectStream(client_send, server_receive)
    server_stream = StapledObjectStream(server_send, client_receive)

    async def serve():
        try:
            async with await TLSStream.wrap(
                server_stream, server_side=True, ssl_context=server_context, standard_compatible=False
            ) as stream:
                await stream.send((await stream.receive())[::-1])
        except ssl.SSLError:
            # The client sends a TLS alert when it rejects the hostname.
            if certificate_hostname == "xn--fa-hia.de":
                raise

    with anyio.fail_after(5):
        async with anyio.create_task_group() as tasks:
            tasks.start_soon(serve)
            if certificate_hostname == "xn--fa-hia.de":
                async with await TLSStream.wrap(
                    client_stream, hostname="faß.de", ssl_context=client_context, standard_compatible=False
                ) as stream:
                    await stream.send(b"sahool")
                    assert await stream.receive() == b"loohas"
            else:
                with pytest.raises(ssl.SSLCertVerificationError):
                    await TLSStream.wrap(
                        client_stream, hostname="faß.de", ssl_context=client_context, standard_compatible=False
                    )
            tasks.cancel_scope.cancel()


def test_shared_crypto_encryption_roundtrip_and_tamper_rejection(monkeypatch):
    """Exercise the actual SQLAlchemy consumer's AES-GCM data format."""
    repo = Path(__file__).resolve().parents[3]
    spec = importlib.util.spec_from_file_location(
        "_dependency_regression_crypto", repo / "packages/shared-crypto/src/sqlalchemy_encryption.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setenv("ENCRYPTION_KEY", "12" * 32)
    encrypted = module.encrypt_field("حقل سري 123")
    assert module.decrypt_field(encrypted) == "حقل سري 123"
    nonce, payload = encrypted.split(":")
    ciphertext = bytearray(base64.b64decode(payload))
    ciphertext[-1] ^= 1
    with pytest.raises(ValueError, match="Decryption failed"):
        module.decrypt_field(nonce + ":" + base64.b64encode(ciphertext).decode())
    signature = module.create_hmac("field-123", secret="test-only-hmac-key")
    assert module.verify_hmac("field-123", signature, secret="test-only-hmac-key")
    assert not module.verify_hmac("field-124", signature, secret="test-only-hmac-key")


class _NestedDatabaseSettings(BaseModel):
    passwd: str | None = None


def _load_nested_secrets(directory: Path, max_size: int = 100):
    class Settings(BaseSettings):
        model_config = SettingsConfigDict(
            secrets_dir=directory,
            secrets_nested_subdir=True,
            secrets_dir_max_size=max_size,
        )
        db: _NestedDatabaseSettings = _NestedDatabaseSettings()

        @classmethod
        def settings_customise_sources(
            cls, settings_cls, init_settings, env_settings, dotenv_settings, file_secret_settings
        ):
            return (NestedSecretsSettingsSource(file_secret_settings),)

    return Settings()


def test_nested_settings_cannot_read_secrets_through_an_external_directory_symlink(tmp_path):
    """CVE-2026-58203: a writable mount must not expose a file outside secrets_dir."""
    secrets = tmp_path / "secrets"
    outside = tmp_path / "outside"
    secrets.mkdir()
    outside.mkdir()
    (outside / "passwd").write_text("outside-secret" * 40)
    (secrets / "db").symlink_to(outside, target_is_directory=True)
    assert _load_nested_secrets(secrets).db.passwd is None


def test_nested_settings_load_regular_in_directory_secrets(tmp_path):
    database = tmp_path / "db"
    database.mkdir()
    (database / "passwd").write_text("local-test-secret")
    assert _load_nested_secrets(tmp_path).db.passwd == "local-test-secret"


def test_nested_settings_enforce_the_loading_size_limit(tmp_path):
    database = tmp_path / "db"
    database.mkdir()
    (database / "passwd").write_text("x" * 101)
    with pytest.raises(SettingsError, match="secrets_dir size is above 100 bytes"):
        _load_nested_secrets(tmp_path, max_size=100)


def test_ai_advisor_settings_preserve_typed_environment_overrides(monkeypatch, tmp_path):
    """Exercise a real service's environment parsing without importing its model stack."""
    repo = Path(__file__).resolve().parents[3]
    spec = importlib.util.spec_from_file_location(
        "_dependency_regression_advisor_settings", repo / "apps/services/ai-advisor/src/config.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # Isolate .env file discovery while retaining the consumer's real Settings class.
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SERVICE_PORT", "9123")
    monkeypatch.setenv("ENABLE_CACHE", "false")
    spec.loader.exec_module(module)
    assert module.settings.service_port == 9123
    assert module.settings.enable_cache is False
    monkeypatch.setenv("SERVICE_PORT", "not-a-port")
    with pytest.raises(ValidationError):
        module.Settings()
