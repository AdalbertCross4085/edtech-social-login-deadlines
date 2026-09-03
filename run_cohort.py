#!/usr/bin/env python3
"""Sign one learner in through the callback, then print the educator view.

    INFRAI_API_KEY=... python run_cohort.py <challenge-token>
"""
from __future__ import annotations

import sys
from datetime import date, timedelta

from course_delivery import CS_INTRO
from educator_report import cohort_report, render
from oauth_callback import CallbackRequest, SignInRejected, sign_in


def main() -> int:
    token = sys.argv[1] if len(sys.argv) > 1 else ""
    if not token:
        print("usage: python run_cohort.py <challenge-token>", file=sys.stderr)
        return 2

    request = CallbackRequest(
        provider="github",
        provider_account_id="4812",
        email="mira@example.edu",
        display_name="Mira Okafor",
        challenge_token=token,
        client_ip="203.0.113.7",
    )
    try:
        enrolment = sign_in(request, CS_INTRO, today=date.today() - timedelta(days=20))
    except SignInRejected as rejected:
        print(f"HTTP {rejected.status} {rejected.code}: {rejected.message}", file=sys.stderr)
        return 1

    print(f"enrolled {enrolment.learner.learner_id} in {enrolment.course.code}")
    for deadline in enrolment.deadlines:
        print(f"  {deadline.module_slug:<16} unlocks {deadline.unlocks_on} due {deadline.due_on}")
    print()
    print(render(cohort_report([enrolment], today=date.today())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
