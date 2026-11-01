"""Real runtime acceptance for the frozen root extras.

Run explicitly with pytest, outside default test discovery:
    python -m pytest scripts/ci/check_python_lock_runtime.py --junitxml=runtime.xml

All dependencies are mandatory here. These tests exercise local cryptography,
image decoding, and CPU inference; they do not download models or contact services.
"""

from __future__ import annotations

import io
from datetime import UTC, datetime, timedelta

import pytest


@pytest.fixture(scope="module", params=["RS256", "ES256"])
def signing_keys(request):
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ec, rsa

    def generate():
        if request.param == "RS256":
            return rsa.generate_private_key(public_exponent=65537, key_size=2048)
        return ec.generate_private_key(ec.SECP256R1())

    key = generate()
    private = key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
    )
    public = key.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
    wrong_public = (
        generate()
        .public_key()
        .public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
    )
    return request.param, private, public, wrong_public


@pytest.fixture
def claims():
    now = datetime.now(UTC)
    return {
        "sub": "local-test-user",
        "iss": "sahool-test",
        "aud": "local-client",
        "iat": now,
        "exp": now + timedelta(minutes=5),
    }


def test_jwt_asymmetric_round_trip(signing_keys, claims):
    import jwt

    algorithm, private, public, _ = signing_keys
    token = jwt.encode(claims, private, algorithm=algorithm)
    decoded = jwt.decode(token, public, algorithms=[algorithm], issuer="sahool-test", audience="local-client")
    assert decoded["sub"] == claims["sub"]


def test_jwt_wrong_key_rejected(signing_keys, claims):
    import jwt

    algorithm, private, _, wrong_public = signing_keys
    token = jwt.encode(claims, private, algorithm=algorithm)
    with pytest.raises(jwt.InvalidSignatureError):
        jwt.decode(token, wrong_public, algorithms=[algorithm], issuer="sahool-test", audience="local-client")


def test_jwt_modified_payload_rejected(signing_keys, claims):
    import jwt

    algorithm, private, public, _ = signing_keys
    token = jwt.encode(claims, private, algorithm=algorithm)
    header, _, signature = token.split(".")
    changed_payload = jwt.utils.base64url_encode(b'{"sub":"forged-admin"}').decode()
    with pytest.raises(jwt.InvalidSignatureError):
        jwt.decode(f"{header}.{changed_payload}.{signature}", public, algorithms=[algorithm], audience="local-client")


def test_jwt_expired_token_rejected(signing_keys, claims):
    import jwt

    algorithm, private, public, _ = signing_keys
    token = jwt.encode({**claims, "exp": datetime.now(UTC) - timedelta(seconds=1)}, private, algorithm=algorithm)
    with pytest.raises(jwt.ExpiredSignatureError):
        jwt.decode(token, public, algorithms=[algorithm], issuer="sahool-test", audience="local-client")


def test_jwt_public_key_cannot_be_hmac_secret(signing_keys, claims):
    import jwt

    _, _, public, _ = signing_keys
    with pytest.raises(jwt.InvalidKeyError):
        jwt.encode(claims, public, algorithm="HS256")


def test_passlib_password_hash_round_trip():
    from passlib.context import CryptContext

    context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed = context.hash("synthetic-password-42")
    assert context.verify("synthetic-password-42", hashed)
    assert not context.verify("wrong-password", hashed)


def _http_test_app():
    from fastapi import FastAPI, HTTPException

    app = FastAPI()

    @app.post("/echo", response_model=dict[str, int])
    def echo(body: dict[str, int]):
        return body

    @app.get("/unauthorized")
    def unauthorized():
        raise HTTPException(status_code=401, detail="invalid token")

    return app


def test_fastapi_starlette_request_validation_and_errors():
    from fastapi.testclient import TestClient

    with TestClient(_http_test_app()) as client:
        response = client.post("/echo", json={"value": 42})
        assert response.status_code == 200 and response.json() == {"value": 42}
        assert client.post("/echo", json={"value": "not an integer"}).status_code == 422
        rejected = client.get("/unauthorized")
        assert rejected.status_code == 401 and rejected.json() == {"detail": "invalid token"}


def test_opentelemetry_fastapi_spans_and_trace_context():
    from fastapi.testclient import TestClient
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
    from opentelemetry.sdk.trace.sampling import ALWAYS_ON
    from opentelemetry.trace import SpanKind

    app = _http_test_app()
    exporter = InMemorySpanExporter()
    # Own sampling as well as the in-memory sink; host telemetry settings must
    # not probabilistically omit the request under test.
    provider = TracerProvider(sampler=ALWAYS_ON)
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)
    try:
        with TestClient(app) as client:
            response = client.post(
                "/echo",
                json={"value": 42},
                headers={"traceparent": "00-0123456789abcdef0123456789abcdef-0123456789abcdef-01"},
            )
            assert response.status_code == 200
            assert client.get("/unauthorized").status_code == 401
        provider.force_flush()
        spans = [span for span in exporter.get_finished_spans() if span.kind == SpanKind.SERVER]
        assert any(span.context.trace_id == int("0123456789abcdef0123456789abcdef", 16) for span in spans)
        statuses = {
            span.attributes.get("http.response.status_code", span.attributes.get("http.status_code")) for span in spans
        }
        assert {200, 401} <= statuses
    finally:
        FastAPIInstrumentor.uninstrument_app(app)
        provider.shutdown()


@pytest.mark.parametrize("format_name", ["PNG", "JPEG"])
def test_image_decode_round_trip(format_name):
    import numpy as np
    from PIL import Image

    source = Image.new("RGB", (16, 16), (20, 160, 40))
    stream = io.BytesIO()
    source.save(stream, format=format_name)
    stream.seek(0)
    with Image.open(stream) as decoded:
        decoded.load()
        assert decoded.format == format_name
        actual = np.asarray(decoded.convert("RGB"), dtype=np.float32)
    assert actual.shape == (16, 16, 3)
    np.testing.assert_allclose(actual, np.asarray(source, dtype=np.float32), atol=2 if format_name == "JPEG" else 0)


@pytest.mark.parametrize("format_name", ["PNG", "JPEG"])
def test_image_truncation_rejected(format_name):
    from PIL import Image

    stream = io.BytesIO()
    Image.new("RGB", (16, 16), (20, 160, 40)).save(stream, format=format_name)
    with pytest.raises(OSError), Image.open(io.BytesIO(stream.getvalue()[:24])) as decoded:
        decoded.load()


def test_image_invalid_bytes_rejected():
    from PIL import Image, UnidentifiedImageError

    with pytest.raises(UnidentifiedImageError):
        Image.open(io.BytesIO(b"this is not an image"))


def test_image_pixel_limit_remains_enforced(monkeypatch):
    from PIL import Image

    stream = io.BytesIO()
    Image.new("RGB", (16, 16)).save(stream, format="PNG")
    monkeypatch.setattr(Image, "MAX_IMAGE_PIXELS", 64)
    with pytest.raises(Image.DecompressionBombError):
        Image.open(io.BytesIO(stream.getvalue()))


def test_actual_disease_image_consumer():
    from PIL import Image

    from apps.kernel.common.queue.tasks.disease_detection import analyze_image_colors

    analysis = analyze_image_colors(Image.new("RGB", (16, 16), (20, 160, 40)))
    assert analysis["green_ratio"] == 1.0
    assert 70 <= analysis["mean_hue"] <= 150
    assert analysis["mean_brightness"] == 160.0


def test_tensorflow_numpy_matrix_operation():
    import numpy as np
    import tensorflow as tf

    values = np.asarray([[1, 2], [3, 4]], dtype=np.float32)
    actual = tf.linalg.matmul(tf.constant(values), tf.constant(values)).numpy()
    np.testing.assert_allclose(actual, np.asarray([[7, 10], [15, 22]], dtype=np.float32))


def test_tensorflow_ml_dtypes_numpy_interoperation():
    import ml_dtypes
    import numpy as np
    import tensorflow as tf

    values = np.asarray([1.0, 2.0, 3.0], dtype=ml_dtypes.bfloat16)
    result = tf.cast(tf.constant(values), tf.float32).numpy()
    np.testing.assert_array_equal(result, np.asarray([1, 2, 3], dtype=np.float32))


def test_keras_inference_and_model_round_trip(tmp_path):
    import numpy as np
    import tensorflow as tf

    model = tf.keras.Sequential(
        [tf.keras.Input(shape=(2,)), tf.keras.layers.Dense(1, use_bias=False, kernel_initializer="ones")]
    )
    inputs = np.asarray([[2, 3], [5, 7]], dtype=np.float32)
    expected = np.asarray([[5], [12]], dtype=np.float32)
    np.testing.assert_allclose(model(inputs, training=False).numpy(), expected)
    path = tmp_path / "synthetic-model.keras"
    model.save(path)
    restored = tf.keras.models.load_model(path)
    np.testing.assert_allclose(restored(inputs, training=False).numpy(), expected)
