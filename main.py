"""Application entrypoint."""

import uvicorn

from config import settings
from core.logging_setup import setup_logging

setup_logging()


if __name__ == "__main__":
    uvicorn.run(
        "api.app:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
