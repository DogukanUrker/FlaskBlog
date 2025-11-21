"""
Encryption Utility

This module provides Fernet encryption/decryption for sensitive data
like SMTP passwords that need to be stored securely but retrieved later.
"""

import base64
import hashlib
from cryptography.fernet import Fernet
from settings import Settings
from utils.log import Log


class EncryptionUtil:
    """
    Provides symmetric encryption using Fernet.
    Uses the app's secret key to derive an encryption key.
    """

    _fernet = None

    @classmethod
    def _get_fernet(cls):
        """
        Get or create the Fernet instance using the app's secret key.

        Returns:
            Fernet: The Fernet encryption instance
        """
        if cls._fernet is None:
            # Derive a 32-byte key from the app secret key using SHA-256
            key = hashlib.sha256(Settings.APP_SECRET_KEY.encode()).digest()
            # Fernet requires base64-encoded 32-byte key
            fernet_key = base64.urlsafe_b64encode(key)
            cls._fernet = Fernet(fernet_key)
        return cls._fernet

    @classmethod
    def encrypt(cls, plaintext: str) -> str:
        """
        Encrypt a plaintext string.

        Args:
            plaintext (str): The text to encrypt

        Returns:
            str: The encrypted text (base64 encoded)
        """
        if not plaintext:
            return ""

        try:
            fernet = cls._get_fernet()
            encrypted = fernet.encrypt(plaintext.encode())
            return encrypted.decode()
        except Exception as e:
            Log.error(f"Encryption failed: {e}")
            return ""

    @classmethod
    def decrypt(cls, ciphertext: str) -> str:
        """
        Decrypt an encrypted string.

        Args:
            ciphertext (str): The encrypted text (base64 encoded)

        Returns:
            str: The decrypted plaintext
        """
        if not ciphertext:
            return ""

        try:
            fernet = cls._get_fernet()
            decrypted = fernet.decrypt(ciphertext.encode())
            return decrypted.decode()
        except Exception as e:
            Log.error(f"Decryption failed: {e}")
            # Return empty string if decryption fails (e.g., old unencrypted data)
            return ""
