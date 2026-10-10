import pytest
from cryptography.fernet import Fernet

from app.core.crypto import DecryptionError, EncryptionNotConfiguredError, TokenCipher


def test_roundtrip_and_ciphertext_differs():
    cipher = TokenCipher.from_settings()
    token = "IGAA-example-access-token"
    encrypted = cipher.encrypt(token)
    assert encrypted != token and token not in encrypted
    assert cipher.decrypt(encrypted) == token


def test_missing_key_is_explicit_error():
    with pytest.raises(EncryptionNotConfiguredError):
        TokenCipher([])


def test_invalid_key_is_explicit_error():
    with pytest.raises(EncryptionNotConfiguredError):
        TokenCipher(["not-a-fernet-key"])


def test_wrong_key_cannot_decrypt():
    a = TokenCipher([Fernet.generate_key().decode()])
    b = TokenCipher([Fernet.generate_key().decode()])
    with pytest.raises(DecryptionError):
        b.decrypt(a.encrypt("secret"))


def test_key_rotation():
    old, new = Fernet.generate_key().decode(), Fernet.generate_key().decode()
    legacy = TokenCipher([old]).encrypt("secret")
    rotating = TokenCipher([new, old])
    assert rotating.decrypt(legacy) == "secret"
    rotated = rotating.rotate(legacy)
    assert TokenCipher([new]).decrypt(rotated) == "secret"
