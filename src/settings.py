import os

SERVICE_HOST = os.environ.get("SERVICE_HOST", "0.0.0.0")
SERVICE_PORT = int(os.environ.get("SERVICE_PORT", "8000"))
SERVICE_LOG_LEVEL = os.environ.get("SERVICE_LOG_LEVEL", "info")