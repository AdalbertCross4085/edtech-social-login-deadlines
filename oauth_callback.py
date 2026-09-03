"""OAuth callback: challenge check, then enrolment."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional

from course_delivery import Course, Enrolment, Learner, Provider, enrol
from infrai_captcha import CaptchaCheck, InfraiError, verify_captcha


@dataclass(frozen=True)
class CallbackRequest:
    """What the browser posts back after Google/GitHub redirects."""

    provider: Provider
    provider_account_id: str
    email: str
    display_name: str
    challenge_token: str
    client_ip: Optional[str] = None


class SignInRejected(Exception):
    """The challenge did not clear; map this to a 4xx for the browser."""

    def __init__(self, status: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message


def sign_in(request: CallbackRequest, course: Course, today: date) -> Enrolment:
    check = CaptchaCheck(
        token=request.challenge_token,
        vendor="turnstile",
        ip=request.client_ip,
        action=f"login:{request.provider}",
        score_threshold=0.5,
    )
    try:
        result = verify_captcha(check)
    except InfraiError as err:
        raise SignInRejected(403, err.code, str(err)) from err

    if not result.get("success", True):
        raise SignInRejected(403, "CHALLENGE_NOT_PASSED",
                             "sign-in challenge was not cleared")

    learner = Learner(
        email=request.email,
        display_name=request.display_name,
        provider=request.provider,
        provider_account_id=request.provider_account_id,
    )
    return enrol(learner, course, started_on=today)
