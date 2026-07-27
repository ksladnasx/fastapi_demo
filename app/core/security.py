import base64
import binascii
import hashlib
import hmac
import json
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from app.core.config import settings


def verify_api_key(api_key: str, expected_api_key: str) -> bool:
    return secrets.compare_digest(api_key, expected_api_key)


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    iterations = 100_000
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    ).hex()
    return f"pbkdf2_sha256${iterations}${salt}${digest}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations, salt, expected_digest = password_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            int(iterations),
        ).hex()
    except (TypeError, ValueError):
        return False

    return secrets.compare_digest(digest, expected_digest)


def create_access_token(subject: str) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    header = {
        "alg": "HS256",
        "typ": "JWT",
    }
    payload = {
        "sub": subject,  # 用户 id
        "exp": int(expire.timestamp()),  # 过期时间
    }
    encoded_header = _urlsafe_b64encode(
        json.dumps(header, separators=(",", ":")).encode("utf-8")
    )
    payload_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    encoded_payload = _urlsafe_b64encode(payload_bytes)
    signing_input = f"{encoded_header}.{encoded_payload}"

    # 后端用 SECRET_KEY 对 header 和 payload 签名，防止客户端篡改 token 内容。
    signature = hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        signing_input.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return f"{signing_input}.{_urlsafe_b64encode(signature)}"


def decode_access_token(token: str) -> dict[str, Any] | None:
    try:
        encoded_header, encoded_payload, encoded_signature = token.split(".", 2)
    except ValueError:
        return None

    signing_input = f"{encoded_header}.{encoded_payload}"
    expected_signature = hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        signing_input.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    try:
        actual_signature = _urlsafe_b64decode(encoded_signature)
    except (binascii.Error, ValueError):
        return None

    if not secrets.compare_digest(expected_signature, actual_signature):
        return None

    try:
        header = json.loads(_urlsafe_b64decode(encoded_header))
        payload = json.loads(_urlsafe_b64decode(encoded_payload))
    except (binascii.Error, json.JSONDecodeError, ValueError):
        return None

    if header.get("alg") != "HS256" or header.get("typ") != "JWT":
        return None

    if payload.get("exp", 0) < int(datetime.now(UTC).timestamp()):
        return None

    return payload


def _urlsafe_b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _urlsafe_b64decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)
