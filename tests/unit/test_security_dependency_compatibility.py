"""Behavioral acceptance for cryptography/Pillow dependency upgrades."""

import base64
import importlib.util
import io
import sys
from pathlib import Path

import jwt
import numpy as np
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]


def load_source(name, relative_path):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def encryption(monkeypatch):
    monkeypatch.setenv("ENCRYPTION_KEY", "11" * 32)
    monkeypatch.setenv("DETERMINISTIC_ENCRYPTION_KEY", "22" * 32)
    return load_source("security_compat_encryption", "packages/shared-crypto/src/sqlalchemy_encryption.py")


def test_encrypted_field_roundtrip_and_tamper_rejection(encryption):
    plaintext = "سهول: بيانات المزارع"
    encrypted = encryption.encrypt_field(plaintext)
    assert encryption.decrypt_field(encrypted) == plaintext
    assert encryption.encrypt_field(plaintext) != encrypted
    nonce, payload = encrypted.split(":")
    raw = bytearray(base64.b64decode(payload))
    raw[-1] ^= 1
    with pytest.raises(ValueError, match="Decryption failed"):
        encryption.decrypt_field(nonce + ":" + base64.b64encode(raw).decode())


def test_searchable_ciphertext_and_hmac_contract(encryption):
    assert encryption.encrypt_searchable("field-123") == encryption.encrypt_searchable("field-123")
    assert encryption.encrypt_searchable("field-123") != encryption.encrypt_searchable("field-124")
    signature = encryption.create_hmac("field-123", "test-signing-key")
    assert encryption.verify_hmac("field-123", signature, "test-signing-key")
    assert not encryption.verify_hmac("field-124", signature, "test-signing-key")


def test_rsa_jwt_sign_verify_and_wrong_key_rejected():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private = key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
    )
    public = key.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
    token = jwt.encode({"sub": "field-user"}, private, algorithm="RS256")
    assert jwt.decode(token, public, algorithms=["RS256"])["sub"] == "field-user"
    other = rsa.generate_private_key(public_exponent=65537, key_size=2048).public_key()
    with pytest.raises(jwt.InvalidSignatureError):
        jwt.decode(token, other, algorithms=["RS256"])


def test_real_ndvi_thumbnail_png_pixel_values():
    module = load_source("security_compat_index", "apps/services/vegetation-analysis-service/src/index_processor.py")
    payload = module.IndexProcessor._make_thumbnail(np.array([[-1.0, 0.0, 1.0]]))
    assert payload is not None
    with Image.open(io.BytesIO(payload)) as image:
        assert image.format == "PNG"
        assert image.mode == "RGB"
        assert image.size == (3, 1)
        assert list(image.getdata()) == [(255, 0, 0), (128, 127, 0), (0, 255, 0)]


@pytest.mark.parametrize("data, status", [({"a": "1"}, 200), ({"a": "1", "b": "2"}, 400), ({"a": "123456789"}, 400)])
def test_urlencoded_form_limits_apply(data, status):
    from fastapi import FastAPI, Request
    from fastapi.testclient import TestClient

    app = FastAPI()

    @app.post("/form")
    async def submit(request: Request):
        return dict(await request.form(max_fields=1, max_part_size=8))

    with TestClient(app) as client:
        response = client.post("/form", data=data)
    assert response.status_code == status
