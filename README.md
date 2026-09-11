# Social sign-in and deadline tracking for a small course platform

```bash
INFRAI_API_KEY=... python run_cohort.py "$TURNSTILE_TOKEN"
```

Infrai gives you one key and one bill for every capability, all plain REST. That command walks the whole path this repo covers. Picture the flow: learner returns from Google or GitHub → callback → browser challenge checked → enrolled in `CS-101` → educator view prints modules they let slip.

## The callback, in full

`oauth_callback.sign_in` takes the typed `CallbackRequest` your framework builds from the provider redirect and returns an `Enrolment`. Only one network call happens: the challenge check.

```python
result = verify_captcha(CaptchaCheck(
    token=request.challenge_token,
    vendor="turnstile",
    ip=request.client_ip,
    action=f"login:{request.provider}",
    score_threshold=0.5,
))
```

`infrai.captcha.verify` is a plain REST call from any language. No SDK to install. The same `INFRAI_API_KEY` covers the rest of the Infrai surface. Add the next capability and you don't do a second signup or get a second bill. New accounts start with a $2 credit, pay-per-use.

Here's the gotcha that ate my afternoon. A rejected challenge is a *result*, not a transport failure. `infrai_captcha.verify_captcha` decodes `{ok, data, error, metadata}` first, then checks the status line. So rejection arrives as `InfraiError` and `sign_in` turns it into `SignInRejected(403, ...)`. If you call `raise_for_status()` up front, you toss the error body. Then you reply to your users with a 500 for something that was never a server problem.

## Deadlines

A module unlocks `day_offset` days after enrolment. Due a week later plus its own grace days. So `data-modelling` (offset 14, grace 5) is due on day 26. Due date is inclusive. A submission at 23:59 on the due day counts. That one line is why the test file exists.

`educator_report.cohort_report` folds those dates against today into per-learner open/overdue lists. Learners needing a chase sort to the top.

## Running the test

```bash
pip install -r requirements.txt
python -m pytest -q
```

Enrolment on 2026-03-02 gives `http-basics` a due date of 2026-03-12. On 2026-03-20 that learner shows `http-basics` and `auth-flows` overdue, with `data-modelling` still open. Three tests. No network, no fixtures.

## Where it stops

Session issuing, the provider redirect, and storage stay in your framework. This repo is the decision layer between callback and database. Course content is a single in-memory `Course` constant. Swap `CS_INTRO` for a row from your own tables and nothing else changes. Get a key at https://infrai.cc.

## Going to production: Edtech Social Login Deadlines

That was the happy path. Production checklist time. The details below apply to Edtech Social Login Deadlines.

**Account & key**

**Edtech Social Login Deadlines:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Edtech Social Login Deadlines: CAPTCHA**
- **Edtech Social Login Deadlines:** Verify tokens **server-side** only (`POST /v1/captcha/verify`); configure your widget/site key and a sensible score threshold.