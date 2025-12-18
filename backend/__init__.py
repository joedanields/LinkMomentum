"""
Deprecated `backend` compatibility shim.
Code was reorganized into the `app` package. This module re-exports
the main symbols to preserve backward compatibility for imports
that still reference `backend`.
"""
from warnings import warn
warn("'backend' package is deprecated; use 'app' package modules instead.", DeprecationWarning)

from app.db import *  # noqa: F401,F403
from app.image_processor import ImageProcessor  # noqa: F401
from app.linkedin_api import LinkedInAPI  # noqa: F401
