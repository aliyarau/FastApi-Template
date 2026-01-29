"""Logging setup for console and file handlers."""

import asyncio
import gzip
import logging
import logging.handlers
import os
import shutil
import sys
from pathlib import Path
from types import TracebackType
from typing import Any, cast

from config import settings
from config.settings import BASE_DIR, LoggingConfig


class RequestIdFilter(logging.Filter):
    """Ensure request_id is present on log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return True


def setup_logging() -> None:
    """Configure application logging."""
    log_cfg = cast(LoggingConfig, settings.log)
    level = getattr(logging, log_cfg.level.upper(), logging.INFO)

    fmt = "%(asctime)s | %(levelname)s | %(process)d | %(pathname)s:%(lineno)d | rid=%(request_id)s | %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    log_dir = Path(log_cfg.file).parent if log_cfg.file else (BASE_DIR / "var" / "log")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = Path(log_cfg.file) if log_cfg.file else (log_dir / "app.log")

    console = logging.StreamHandler()
    fileh = logging.handlers.TimedRotatingFileHandler(
        filename=str(log_file),
        when="midnight",
        interval=1,
        backupCount=log_cfg.retention_days,
        encoding="utf-8",
        utc=False,
    )

    def namer(name: str) -> str:
        return name + ".gz"

    def rotator(source: str, dest: str) -> None:
        with open(source, "rb") as sf, gzip.open(dest, "wb") as df:
            shutil.copyfileobj(sf, df)
        os.remove(source)

    fileh.namer = namer
    fileh.rotator = rotator

    req_filter = RequestIdFilter()
    console.addFilter(req_filter)
    fileh.addFilter(req_filter)

    logging.basicConfig(
        level=level,
        format=fmt,
        datefmt=datefmt,
        handlers=[console, fileh],
        force=True,
    )

    logging.getLogger("sqlalchemy").setLevel(getattr(logging, log_cfg.sa_level.upper(), logging.WARNING))

    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        lg = logging.getLogger(name)
        lg.handlers.clear()
        lg.propagate = True

    _install_global_exception_logging()
    _install_asyncio_exception_logging()


def _install_global_exception_logging() -> None:
    def _hook(
        exc_type: type[BaseException],
        exc: BaseException,
        tb: TracebackType | None,
    ) -> None:
        logging.critical("UNHANDLED EXCEPTION", exc_info=(exc_type, exc, tb))

    sys.excepthook = _hook


def _install_asyncio_exception_logging() -> None:
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        return

    def _handle(_loop: asyncio.AbstractEventLoop, context: dict[str, Any]) -> None:
        msg = context.get("message", "asyncio error")
        exc = context.get("exception")
        if exc:
            logging.critical("UNHANDLED ASYNCIO EXCEPTION: %s", msg, exc_info=exc)
        else:
            logging.critical("UNHANDLED ASYNCIO ERROR: %s", msg)

    loop.set_exception_handler(_handle)
