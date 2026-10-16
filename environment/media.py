import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(interpolate=True)

# Where downloaded post images are written to disk - mounted as a docker
# volume in production, overridable locally the same way LOG_PATH is.
MEDIA_PATH = Path(os.getenv("MEDIA_PATH", "/var/lib/app/media"))
MEDIA_PATH.mkdir(parents=True, exist_ok=True)

# URL prefix the images are served under - backend.py mounts MEDIA_PATH here.
MEDIA_URL_PREFIX = "/media"
