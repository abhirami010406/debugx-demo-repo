import sys
import traceback
from typing import Optional

import requests


class DebugXClient:
    def __init__(
        self,
        endpoint: str = "http://127.0.0.1:8000/api/ingest",
        service_name: Optional[str] = None,
        environment: Optional[str] = None,
        repository: Optional[str] = None,
        branch: str = "main",
        commit_sha: Optional[str] = None,
    ):
        self.endpoint = endpoint
        self.service_name = service_name
        self.environment = environment
        self.repository = repository
        self.branch = branch
        self.commit_sha = commit_sha

    def report_exception(
        self,
        exc_type,
        exc_value,
        exc_traceback,
        method: str = "GET",
        endpoint: str = "/",
        status_code: int = 500,
    ):
        stack_trace = "".join(
            traceback.format_exception(
                exc_type,
                exc_value,
                exc_traceback,
            )
        )

        error_type = getattr(
            exc_type,
            "__name__",
            "UnknownError",
        )

        payload = {
            "method": method,
            "endpoint": endpoint,
            "status_code": status_code,
            "error_type": error_type,
            "error_message": str(exc_value),
            "stack_trace": stack_trace,
            "source_file": None,
            "service_name": self.service_name,
            "environment": self.environment,
            "repository": self.repository,
            "commit_sha": self.commit_sha,
            "branch": self.branch,
        }

        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                timeout=10,
            )

            response.raise_for_status()

            print(
                "[DebugX] Incident reported successfully."
            )

            return response.json()

        except requests.RequestException as debugx_error:

            print(
                f"[DebugX] Failed to report incident: "
                f"{debugx_error}"
            )

            return None


def install_global_exception_handler(client: DebugXClient):

    original_hook = sys.excepthook

    def debugx_exception_hook(
        exc_type,
        exc_value,
        exc_traceback,
    ):

        client.report_exception(
            exc_type,
            exc_value,
            exc_traceback,
        )

        original_hook(
            exc_type,
            exc_value,
            exc_traceback,
        )

    sys.excepthook = debugx_exception_hook
