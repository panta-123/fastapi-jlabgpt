import os
import uuid
from datetime import datetime


def unique_filename(filename: str) -> str:
    """Generate a unique filename using UUID and timestamp."""
    base, ext = os.path.splitext(filename)
    unique_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex}"
    return f"{base}_{unique_id}{ext}"
