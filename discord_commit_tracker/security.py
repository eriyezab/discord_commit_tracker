import hashlib
import hmac


def verify_signature(body: bytes, secret: str, signature_header: str | None) -> bool:
    if not signature_header:
        return False
    expected = hmac.new(secret.encode(), body, hashlib.sha256)
    expected_sig = f"sha256={expected.hexdigest()}"
    return hmac.compare_digest(expected_sig, signature_header)
