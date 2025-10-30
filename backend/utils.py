import os
from pathlib import Path


UPLOAD_DIR = Path(__file__).resolve().parents[1] / 'data' / 'uploads'
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


ALLOWED_EXT = {'.jpg', '.jpeg', '.png'}


def save_upload_file_bytes(uploaded_file, dest_path: Path):
with open(dest_path, 'wb') as f:
f.write(uploaded_file)