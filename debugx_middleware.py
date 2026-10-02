
import asyncio
import logging
import os
import traceback
from pathlib import Path
from typing import Callable

import httpx
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


logger = logging.getLogger("debugx.middleware")


class DebugXMiddleware(BaseHTTPMiddleware):
    """
    Agentless DebugX error-capture middleware for FastAPI.

    The middleware observes unhandled application exceptions and
    forwards structured incident information to DebugX without
    allowing DebugX failures to affect the monitored application.
    """

    def __init__(
        self,
        app,
        debugx_url: str | None = None,
        service_name: str | None = None,
        environment: str | None = None,
        repository: str | None = None,
        branch: str | None = None,
        commit_sha: str | None = None,
    ):
        super().__init__(app)

        self.debugx_url = (
            debugx_url
            or os.getenv(
                "DEBUGX_URL",
                "http://127.0.0.1:8000",
            )
        ).rstrip("/")

        self.service_name = (
            service_name
            or os.getenv(
                "DEBUGX_SERVICE",
                "demo-user-service",
            )
        )

        self.environment = (
            environment
            or os.getenv(
                "DEBUGX_ENVIRONMENT",
                "development",
            )
        )

        self.repository = (
            repository
            or os.getenv(
                "DEBUGX_REPOSITORY",
                "abhirami010406/debugx-demo-repo",
            )
        )

        self.branch = (
            branch
            or os.getenv(
                "DEBUGX_BRANCH",
                "main",
            )
        )

        self.commit_sha = (
            commit_sha
            or os.getenv(
                "DEBUGX_COMMIT_SHA",
                "",
            )
        )

        self.ingest_api_key = os.getenv(
            "DEBUGX_INGEST_API_KEY",
            "",
        )

    def _load_source_code(self) -> str:
        """
        Load the source code of the monitored application.

        This allows DebugX to analyze the exact source that
        produced the captured runtime exception.
        """

        source_path = (
            Path(__file__).resolve().parent / "main.py"
        )

        try:
            return source_path.read_text(
                encoding="utf-8"
            )

        except Exception:
            logger.exception(
                "Failed to load monitored source code"
            )
            return ""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ):
        try:
            return await call_next(request)

        except Exception as exc:
            stack_trace = traceback.format_exc()

            payload = {
                "method": request.method,
                "endpoint": request.url.path,
                "status_code": 500,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
                "stack_trace": stack_trace,
                "source_code": self._load_source_code(),
                "service_name": self.service_name,
                "environment": self.environment,
                "repository": self.repository,
                "branch": self.branch,
                "commit_sha": self.commit_sha,
            }

            # Schedule telemetry without making DebugX part
            # of the application's request critical path.
            asyncio.create_task(
                self._send_to_debugx(payload)
            )

            # Preserve the application's original behavior.
            raise

    async def _send_to_debugx(
        self,
        payload: dict,
    ) -> None:
        """
        Send an incident to DebugX.

        Any failure here is intentionally swallowed because
        observability must never become an application failure.
        """

        ingestion_url = f"{self.debugx_url}/api/ingest"

        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(
                    connect=1.0,
                    read=15.0,
                    write=2.0,
                    pool=1.0,
                )
            ) as client:
                await client.post(
                    ingestion_url,
                    headers={
                        "X-DebugX-API-Key": self.ingest_api_key,
                    },
                    json=payload,
                )

        except Exception:
            logger.exception(
                "Failed to send incident to DebugX"
            )
            return
