"""
CrisisSignal AI — Evidence Service
Phase 3: Handles photo/file upload validation and storage for alert evidence.

Uploads are saved to: app/static/uploads/evidence/<alert_id>/<filename>
Validated with Pillow to prevent non-image file spoofing.
Max file size: 5MB. Allowed: jpg, jpeg, png, webp.
"""

import os
import uuid
from pathlib import Path
from flask import current_app
from werkzeug.utils import secure_filename

# Allowed extensions
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_FILE_BYTES = 5 * 1024 * 1024  # 5 MB


def _upload_dir(alert_id):
    """Return absolute path to the upload directory for a given alert."""
    base = Path(current_app.root_path) / "static" / "uploads" / "evidence" / str(alert_id)
    base.mkdir(parents=True, exist_ok=True)
    return base


def _allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


class EvidenceService:
    """Handles evidence photo upload, validation, and path management."""

    @staticmethod
    def save_photo(file_storage, alert_id):
        """
        Validate and save an uploaded photo for a given alert.

        Args:
            file_storage: Werkzeug FileStorage object from request.files
            alert_id: int — used to organise the upload directory

        Returns:
            relative_path (str) — relative to static/, for use in url_for('static', ...)
            OR raises ValueError with a user-friendly message.
        """
        if not file_storage or file_storage.filename == "":
            raise ValueError("No file selected.")

        if not _allowed_file(file_storage.filename):
            raise ValueError(f"File type not allowed. Use: {', '.join(ALLOWED_EXTENSIONS)}")

        # Read bytes to check size and validate with Pillow
        file_bytes = file_storage.read()
        if len(file_bytes) > MAX_FILE_BYTES:
            raise ValueError("File too large. Maximum size is 5 MB.")

        # Validate it's actually an image (not a renamed .exe)
        try:
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(file_bytes))
            img.verify()  # Raises if not a valid image
        except Exception:
            raise ValueError("Invalid image file. Please upload a valid photo.")

        # Generate safe filename: <uuid>.<ext>
        ext = secure_filename(file_storage.filename).rsplit(".", 1)[1].lower()
        safe_name = f"{uuid.uuid4().hex}.{ext}"

        upload_dir = _upload_dir(alert_id)
        abs_path = upload_dir / safe_name
        abs_path.write_bytes(file_bytes)

        # Return path relative to static/ for url_for('static', filename=...)
        relative = f"uploads/evidence/{alert_id}/{safe_name}"
        return relative

    @staticmethod
    def delete_photo(relative_path):
        """Delete an existing photo by its relative path."""
        if not relative_path:
            return
        try:
            abs_path = Path(current_app.root_path) / "static" / relative_path
            if abs_path.exists():
                abs_path.unlink()
        except Exception as e:
            current_app.logger.warning(f"[EvidenceService] Could not delete photo: {e}")
