"""
This module provides Two-Factor Authentication (2FA) functionality using TOTP (Time-based One-Time Password).

It includes utilities for:
- Generating TOTP secrets
- Creating QR codes for authenticator apps
- Verifying TOTP tokens
- Managing backup recovery codes
"""

import base64
import io
import json
import secrets
from typing import List, Tuple

import pyotp
import qrcode
from settings import Settings


class TwoFactorAuth:
    """
    Handles Two-Factor Authentication operations using TOTP.
    """

    @staticmethod
    def generate_secret() -> str:
        """
        Generate a random base32-encoded secret for TOTP.

        Returns:
            str: Base32-encoded secret key
        """
        return pyotp.random_base32()

    @staticmethod
    def get_totp_uri(userName: str, secret: str) -> str:
        """
        Generate a provisioning URI for QR code generation.

        Args:
            userName (str): Username for the account
            secret (str): TOTP secret key

        Returns:
            str: Provisioning URI for authenticator apps
        """
        return pyotp.totp.TOTP(secret).provisioning_uri(
            name=userName, issuer_name="FlaskBlog"
        )

    @staticmethod
    def generate_qr_code(uri: str) -> str:
        """
        Generate a QR code image from a provisioning URI and return it as base64.

        Args:
            uri (str): Provisioning URI

        Returns:
            str: Base64-encoded PNG image of QR code
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64 for HTML display
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        return f"data:image/png;base64,{img_str}"

    @staticmethod
    def verify_token(secret: str, token: str) -> bool:
        """
        Verify a TOTP token against the secret.

        Args:
            secret (str): TOTP secret key
            token (str): 6-digit TOTP code to verify

        Returns:
            bool: True if token is valid, False otherwise
        """
        if not secret or not token:
            return False

        try:
            totp = pyotp.TOTP(secret)
            # Verify with a window of ±1 interval (30 seconds) to account for time skew
            return totp.verify(token, valid_window=1)
        except Exception:
            return False

    @staticmethod
    def generate_backup_codes(count: int = 10) -> List[str]:
        """
        Generate backup recovery codes for account recovery.

        Args:
            count (int): Number of backup codes to generate (default: 10)

        Returns:
            List[str]: List of backup codes
        """
        codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric codes
            code = secrets.token_hex(4).upper()
            # Format as XXXX-XXXX for readability
            formatted_code = f"{code[:4]}-{code[4:]}"
            codes.append(formatted_code)
        return codes

    @staticmethod
    def verify_backup_code(stored_codes: str, provided_code: str) -> Tuple[bool, str]:
        """
        Verify a backup code and remove it from the list if valid.

        Args:
            stored_codes (str): JSON string of stored backup codes
            provided_code (str): Backup code provided by user

        Returns:
            Tuple[bool, str]: (is_valid, updated_codes_json)
        """
        if not stored_codes or not provided_code:
            return False, stored_codes

        try:
            codes = json.loads(stored_codes)
            provided_code = provided_code.strip().upper()

            if provided_code in codes:
                # Remove the used code
                codes.remove(provided_code)
                return True, json.dumps(codes)

            return False, stored_codes
        except Exception:
            return False, stored_codes

    @staticmethod
    def codes_to_json(codes: List[str]) -> str:
        """
        Convert backup codes list to JSON string for database storage.

        Args:
            codes (List[str]): List of backup codes

        Returns:
            str: JSON string of codes
        """
        return json.dumps(codes)

    @staticmethod
    def codes_from_json(codes_json: str) -> List[str]:
        """
        Convert JSON string to backup codes list.

        Args:
            codes_json (str): JSON string of codes

        Returns:
            List[str]: List of backup codes
        """
        try:
            return json.loads(codes_json) if codes_json else []
        except Exception:
            return []
