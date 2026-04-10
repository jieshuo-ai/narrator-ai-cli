"""HTTP client for Narrator AI API.

Wraps httpx with automatic auth headers, error handling, and SSE support.
"""

import json as _json
from typing import Any, Optional

import httpx
from httpx_sse import connect_sse

from narrator_ai.config import get_app_key, get_server, get_timeout
from narrator_ai.models.responses import SUCCESS


class NarratorAPIError(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")


class NarratorClient:
    def __init__(
        self,
        server: Optional[str] = None,
        app_key: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        self.server = server if server is not None else get_server()
        self.app_key = app_key if app_key is not None else get_app_key()
        self.timeout = timeout if timeout is not None else get_timeout()
        self._client: Optional[httpx.Client] = None

    def _get_client(self, **kwargs) -> httpx.Client:
        """Get or create a reusable httpx.Client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.Client(
                timeout=self.timeout,
                headers=self._headers(),
            )
        return self._client

    def _headers(self) -> dict:
        return {"app-key": self.app_key}

    def _url(self, path: str) -> str:
        return f"{self.server}{path}"

    def _handle_response(self, resp: httpx.Response) -> dict:
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise NarratorAPIError(resp.status_code, f"HTTP {resp.status_code}: {resp.text[:200]}") from e
        data = resp.json()
        code = data.get("code", 0)
        if code != SUCCESS:
            raise NarratorAPIError(code, data.get("message", "Unknown error"))
        return data.get("data")

    def get(self, path: str, params: Optional[dict] = None) -> Any:
        client = self._get_client()
        resp = client.get(self._url(path), params=params)
        return self._handle_response(resp)

    def post(
        self,
        path: str,
        json: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> Any:
        client = self._get_client()
        resp = client.post(self._url(path), json=json, params=params)
        return self._handle_response(resp)

    def post_sse(self, path: str, json: Optional[dict] = None):
        """POST with SSE streaming. Yields (event_type, data_dict) tuples."""
        headers = {**self._headers(), "Accept": "text/event-stream"}
        with httpx.Client(timeout=httpx.Timeout(self.timeout, read=300.0)) as c:
            with connect_sse(
                c, "POST", self._url(path), headers=headers, json=json
            ) as sse:
                for event in sse.iter_sse():
                    event_type = event.event or "message"
                    try:
                        event_data = _json.loads(event.data)
                    except (ValueError, TypeError):
                        event_data = {"raw": event.data}
                    yield event_type, event_data

    def delete(self, path: str, params: Optional[dict] = None) -> Any:
        client = self._get_client()
        resp = client.delete(self._url(path), params=params)
        return self._handle_response(resp)

    def upload_file(self, upload_url: str, file_path: str, content_type: str = "application/octet-stream"):
        """Upload file to presigned URL."""
        with open(file_path, "rb") as f:
            with httpx.Client(timeout=httpx.Timeout(connect=self.timeout, read=600.0, write=None, pool=self.timeout)) as c:
                resp = c.put(
                    upload_url,
                    content=f,
                    headers={"Content-Type": content_type},
                )
                try:
                    resp.raise_for_status()
                except httpx.HTTPStatusError as e:
                    raise NarratorAPIError(resp.status_code, f"Upload failed: HTTP {resp.status_code}") from e
                return resp

    def close(self):
        if self._client and not self._client.is_closed:
            self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
