import secrets


def verify_api_key(api_key: str, expected_api_key: str) -> bool:
    return secrets.compare_digest(api_key, expected_api_key)
