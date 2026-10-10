"""Encryption at rest for OAuth tokens and other secrets.

Uses Fernet (AES-128-CBC + HMAC-SHA256). Keys come only from
``TOKEN_ENCRYPTION_KEYS`` (comma-separated). The first key encrypts; all keys
decrypt, which allows key rotation without downtime.

Generate a key:
    python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
"""

from cryptography.fernet import Fernet, InvalidToken, MultiFernet

from app.core.config import get_settings


class EncryptionNotConfiguredError(RuntimeError):
    pass


class DecryptionError(RuntimeError):
    pass


class TokenCipher:
    def __init__(self, keys: list[str]) -> None:
        if not keys:
            raise EncryptionNotConfiguredError(
                "TOKEN_ENCRYPTION_KEYS is not set; cannot store OAuth tokens."
            )
        try:
            self._fernet = MultiFernet([Fernet(k.encode()) for k in keys])
        except (ValueError, TypeError) as exc:
            raise EncryptionNotConfiguredError("TOKEN_ENCRYPTION_KEYS is invalid.") from exc

    @classmethod
    def from_settings(cls) -> "TokenCipher":
        raw = get_settings().token_encryption_keys.get_secret_value()
        return cls([k.strip() for k in raw.split(",") if k.strip()])

    def encrypt(self, plaintext: str) -> str:
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        try:
            return self._fernet.decrypt(ciphertext.encode()).decode()
        except InvalidToken as exc:
            raise DecryptionError("Token could not be decrypted (wrong key or tampered).") from exc

    def rotate(self, ciphertext: str) -> str:
        """Re-encrypt with the current primary key."""
        return self._fernet.rotate(ciphertext.encode()).decode()
