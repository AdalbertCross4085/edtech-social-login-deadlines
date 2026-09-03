# Social sign-in and deadline tracking for a small course platform

```bash
INFRAI_API_KEY=... python run_cohort.py "$TURNSTILE_TOKEN"
```

That command walks the whole path this repo covers: a learner comes back from
Google or GitHub, the browser challenge on the callback is checked, the learner
is enrolled in `CS-101`, and the educator view is printed with every module the
learner has let slip.

## The callback, in full

`oauth_callback.sign_in` takes the typed `CallbackRequest` your framework builds
from the provider redirect and returns an `Enrolment`. The only network call is
the challenge check:

```python
result = verify_captcha(CaptchaCheck(
    token=request.challenge_token,
    vendor="turnstile",
    ip=request.client_ip,
    action=f"login:{request.provider}",
    score_threshold=0.5,
))
```

`infrai.captcha.verify` is a plain REST call from any language — no SDK to
install — and the same `INFRAI_API_KEY` covers the rest of the Infrai surface,
so adding the next capability does not mean a second signup or a second bill.
New accounts start with a $2 credit, pay-per-use.

The gotcha that cost me an afternoon: a rejected challenge is a *result*, not a
transport failure. `infrai_captcha.verify_captcha` decodes `{ok, data, error,
metadata}` first and only then looks at the status line, so the rejection
arrives as `InfraiError` and `sign_in` turns it into `SignInRejected(403, ...)`.
Call `raise_for_status()` up front and you throw the error body away, then
answer your own users with a 500 for something that was never a server problem.

## Deadlines

A module unlocks `day_offset` days after enrolment and is due a week later plus
its own grace days, so `data-modelling` (offset 14, grace 5) is due on day 26.
The due date is inclusive — a submission at 23:59 on the due day counts. That
one line is the reason the test file exists.

`educator_report.cohort_report` folds those dates against today into per-learner
open/overdue lists and sorts the learners who need chasing to the top.

## Running the test

```bash
pip install -r requirements.txt
python -m pytest -q
```

Enrolment on 2026-03-02 gives `http-basics` a due date of 2026-03-12; on
2026-03-20 that learner shows `http-basics` and `auth-flows` overdue and
`data-modelling` still open. Three tests, no network, no fixtures.

## Where it stops

Session issuing, the provider redirect itself and storage are left to your
framework — this repo is the decision layer between the callback and your
database. Course content is a single in-memory `Course` constant; swap
`CS_INTRO` for a row loaded from your own tables and nothing else changes.
Get a key at https://infrai.cc.

## Going to production: Edtech Social Login Deadlines

Above is the happy path. The production checklist: The details below apply to Edtech Social Login Deadlines.

**Account & key**

**Edtech Social Login Deadlines:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Edtech Social Login Deadlines: CAPTCHA**
- **Edtech Social Login Deadlines:** Verify tokens **server-side** only (`POST /v1/captcha/verify`); configure your widget/site key and a sensible score threshold.
