from datetime import date

from course_delivery import CS_INTRO, Learner, enrol, module_state
from educator_report import cohort_report

START = date(2026, 3, 2)
MIRA = Learner(
    email="mira@example.edu",
    display_name="Mira Okafor",
    provider="github",
    provider_account_id="4812",
)


def test_schedule_uses_offset_plus_week_plus_grace():
    deadlines = {d.module_slug: d for d in enrol(MIRA, CS_INTRO, START).deadlines}
    assert deadlines["http-basics"].due_on == date(2026, 3, 12)
    assert deadlines["auth-flows"].unlocks_on == date(2026, 3, 9)
    # data-modelling carries five grace days instead of three.
    assert deadlines["data-modelling"].due_on == date(2026, 3, 28)


def test_due_date_is_inclusive():
    deadline = enrol(MIRA, CS_INTRO, START).deadlines[0]
    assert module_state(deadline, date(2026, 3, 12)) == "open"
    assert module_state(deadline, date(2026, 3, 13)) == "overdue"
    assert module_state(deadline, date(2026, 3, 1)) == "locked"


def test_educator_report_flags_the_overdue_learner():
    enrolment = enrol(MIRA, CS_INTRO, START)
    row = cohort_report([enrolment], today=date(2026, 3, 20))[0]
    assert row.overdue_modules == ["http-basics", "auth-flows"]
    assert row.open_modules == ["data-modelling"]
    assert row.needs_attention is True
