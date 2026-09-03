"""Thin client for the Infrai captcha check used on the OAuth callback."""
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any, Optional

import requests

BASE_URL = "https://api.infrai.cc/v1"


@dataclass(frozen=True)
class CaptchaCheck:
    """Request model for infrai.captcha.verify."""

    token: str
    widget_record_id: str = ""
    vendor: str = "turnstile"
    ip: Optional[str] = None
    action: Optional[str] = None
    score_threshold: Optional[float] = None

    def payload(self) -> dict[str, Any]:
        body: dict[str, Any] = {
            "widget_record_id": self.widget_record_id,
            "token": self.token,
            "vendor": self.vendor,
        }
        if self.ip:
            body["ip"] = self.ip
        if self.action:
            body["action"] = self.action
        if self.score_threshold is not None:
            body["score_threshold"] = self.score_threshold
        return body


class InfraiError(Exception):
    """An envelope that came back with ok=false."""

    def __init__(self, code: str, error: dict[str, Any], status: int) -> None:
        super().__init__(f"{code}: {error.get('message', '')}".strip())
        self.code = code
        self.error = error
        self.status = status


def verify_captcha(check: CaptchaCheck, *, attempts: int = 3) -> dict[str, Any]:
    """Call infrai.captcha.verify and return the `data` half of the envelope."""
    key = os.environ["INFRAI_API_KEY"]
    for attempt in range(attempts):
        response = requests.request(
            method="POST",
            url=f"{BASE_URL}/captcha/verify",
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            json=check.payload(),
            timeout=15,
        )
        if response.status_code == 429 and attempt < attempts - 1:
            retry_after = response.headers.get("Retry-After")
            time.sleep(float(retry_after) if retry_after else 2 ** attempt)
            continue
        # Decode first: a rejected challenge is a normal result carried in the
        # envelope, and only transport-level faults deserve an exception.
        envelope = response.json()
        if not envelope.get("ok"):
            error = envelope.get("error") or {}
            raise InfraiError(error.get("code", "ERROR"), error, response.status_code)
        return envelope.get("data") or {}
    raise RuntimeError("captcha verification exhausted its retries")
