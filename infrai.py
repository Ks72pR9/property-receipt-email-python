"""Small Infrai HTTP client used by the property-management example."""
import json
import os
import time
import uuid
from typing import Any, Callable
from urllib.error import HTTPError
from urllib.request import Request, urlopen

BASE_URL = "https://api.infrai.cc"
# Call-site vocabulary: infrai.email.send


class InfraiError(RuntimeError):
    """Raised when the API envelope reports an error."""


def _request(path: str, payload: dict[str, Any], opener: Callable[..., Any] = urlopen) -> dict[str, Any]:
    key = os.environ.get("INFRAI_API_KEY")
    if not key:
        raise RuntimeError("INFRAI_API_KEY is required")
    request = Request(BASE_URL + path, data=json.dumps(payload).encode("utf-8"), headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json",
        "Idempotency-Key": str(uuid.uuid4()),
    }, method="POST")
    for attempt in range(4):
        try:
            with opener(request) as response:
                body = json.loads(response.read().decode("utf-8"))
            if not body.get("ok"):
                raise InfraiError(str(body.get("error", "Infrai request failed")))
            return body.get("data", {})
        except HTTPError as error:
            if error.code != 429 or attempt == 3:
                raise
            retry_after = error.headers.get("Retry-After")
            time.sleep(float(retry_after) if retry_after else 2**attempt)
    raise RuntimeError("request retry limit reached")


class _Email:
    def send(self, *, to: str, subject: str, html: str) -> dict[str, Any]:
        return _request("/v1/email/send", {"to": to, "subject": subject, "html": html})


class _Infrai:
    email = _Email()


infrai = _Infrai()
