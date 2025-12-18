from dotenv import load_dotenv
import os
from typing import Optional

load_dotenv()

# Application directories
UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
STATIC_DIR: str = os.getenv("STATIC_DIR", "static")
TEMPLATE_DIR: str = os.getenv("TEMPLATE_DIR", "templates")

# Image processing thresholds
QUALITY_THRESHOLD: float = float(os.getenv("QUALITY_THRESHOLD", 0.6))
BLUR_THRESHOLD: int = int(os.getenv("BLUR_THRESHOLD", 100))
DUPLICATE_THRESHOLD: int = int(os.getenv("DUPLICATE_THRESHOLD", 5))

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "css"), exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "js"), exist_ok=True)
os.makedirs(TEMPLATE_DIR, exist_ok=True)

# Lazy imports for services to avoid heavy imports on module load
def get_image_processor():
    from app.image_processor import ImageProcessor
    return ImageProcessor(
        quality_threshold=QUALITY_THRESHOLD,
        blur_threshold=BLUR_THRESHOLD,
        duplicate_threshold=DUPLICATE_THRESHOLD
    )

def get_linkedin_api():
    from app.linkedin_api import LinkedInAPI
    return LinkedInAPI()

# Export optional singletons (created on demand)
_image_processor = None
_linkedin_api = None

def image_processor() -> object:
    global _image_processor
    if _image_processor is None:
        _image_processor = get_image_processor()
    return _image_processor

def linkedin_api() -> object:
    global _linkedin_api
    if _linkedin_api is None:
        _linkedin_api = get_linkedin_api()
    return _linkedin_api
