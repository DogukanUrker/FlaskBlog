"""
This module contains file upload validation utilities for security.
"""

import imghdr
from pathlib import Path
from settings import Settings
from utils.log import Log


class FileUploadValidator:
    """
    Validates file uploads for security purposes.
    """

    # Error code constants
    ERROR_FILE_SIZE_EXCEEDED = "FILE_SIZE_EXCEEDED"
    ERROR_INVALID_FILE_TYPE = "INVALID_FILE_TYPE"
    ERROR_INVALID_IMAGE_FILE = "INVALID_IMAGE_FILE"
    ERROR_FILE_TYPE_MISMATCH = "FILE_TYPE_MISMATCH"
    ERROR_SVG_NOT_SUPPORTED = "SVG_NOT_SUPPORTED"

    @staticmethod
    def validate_file(file, file_data=None):
        """
        Validates uploaded file for security.

        Args:
            file: FileStorage object from request.files
            file_data: Optional bytes data if file already read

        Returns:
            tuple: (is_valid: bool, error_code: str or None, file_data: bytes)
                   error_code will be one of the ERROR_* constants if validation fails

        Raises:
            None - returns validation status instead
        """
        # Check if file exists
        if not file or file.filename == "":
            return True, None, b""  # Empty file is allowed (optional upload)

        # Get file data
        if file_data is None:
            file_data = file.read()
            file.seek(0)  # Reset file pointer

        # Check file size
        if len(file_data) > Settings.MAX_UPLOAD_SIZE:
            max_size_mb = Settings.MAX_UPLOAD_SIZE / (1024 * 1024)
            Log.error(
                f"File upload rejected: size {len(file_data)} bytes exceeds limit of {Settings.MAX_UPLOAD_SIZE} bytes ({max_size_mb:.1f}MB)"
            )
            return False, FileUploadValidator.ERROR_FILE_SIZE_EXCEEDED, None

        # Check file extension
        filename = file.filename.lower()
        file_ext = Path(filename).suffix.lstrip(".")

        if file_ext not in Settings.ALLOWED_UPLOAD_EXTENSIONS:
            Log.error(
                f"File upload rejected: extension '{file_ext}' not in allowed extensions {Settings.ALLOWED_UPLOAD_EXTENSIONS}"
            )
            return (
                False,
                FileUploadValidator.ERROR_INVALID_FILE_TYPE,
                None,
            )

        # Validate file content matches extension (prevent fake extensions)
        detected_type = imghdr.what(None, h=file_data)
        if detected_type is None:
            Log.error(
                f"File upload rejected: could not determine image type for '{filename}'"
            )
            return False, FileUploadValidator.ERROR_INVALID_IMAGE_FILE, None

        # Map detected types to extensions
        type_mapping = {
            "jpeg": ["jpg", "jpeg"],
            "png": ["png"],
            "webp": ["webp"],
        }

        is_valid_type = False
        for img_type, extensions in type_mapping.items():
            if detected_type == img_type and file_ext in extensions:
                is_valid_type = True
                break

        if not is_valid_type:
            Log.error(
                f"File upload rejected: file extension '{file_ext}' does not match detected type '{detected_type}'"
            )
            return (
                False,
                FileUploadValidator.ERROR_FILE_TYPE_MISMATCH,
                None,
            )

        # Additional checks for SVG (if allowed in the future)
        if file_ext == "svg":
            # SVG files need special sanitization as they can contain JavaScript
            Log.warning("SVG upload attempted - currently not supported for security")
            return False, FileUploadValidator.ERROR_SVG_NOT_SUPPORTED, None

        Log.success(
            f"File upload validated: '{filename}' ({len(file_data)} bytes, type: {detected_type})"
        )
        return True, None, file_data

    @staticmethod
    def sanitize_filename(filename):
        """
        Sanitize filename to prevent directory traversal and other attacks.

        Args:
            filename: Original filename

        Returns:
            str: Sanitized filename
        """
        # Get just the filename, remove any path components
        filename = Path(filename).name

        # Remove any non-alphanumeric characters except dots and dashes
        import re

        filename = re.sub(r"[^a-zA-Z0-9._-]", "_", filename)

        # Limit filename length
        if len(filename) > 255:
            name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
            filename = name[: 255 - len(ext) - 1] + "." + ext if ext else name[:255]

        return filename
