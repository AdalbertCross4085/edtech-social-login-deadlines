"""Cohort view an educator opens on a Monday morning."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable

from course_delivery import Enrolment, module_state


@dataclass(frozen=True)
class LearnerRow:
    learner_id: str
    display_name: str
    provider: str
    open_modules: list[str]
    overdue_modules: list[str]

    @property
    def needs_attention(self) -> bool:
        return bool(self.overdue_modules)


def cohort_report(enrolments: Iterable[Enrolment], today: date) -> list[LearnerRow]:
    rows: list[LearnerRow] = []
    for enrolment in enrolments:
        states = {d.module_slug: module_state(d, today) for d in enrolment.deadlines}
        rows.append(
            LearnerRow(
                learner_id=enrolment.learner.learner_id,
                display_name=enrolment.learner.display_name,
                provider=enrolment.learner.provider,
                open_modules=[s for s, st in states.items() if st == "open"],
                overdue_modules=[s for s, st in states.items() if st == "overdue"],
            )
        )
    rows.sort(key=lambda r: (not r.needs_attention, r.display_name))
    return rows


def render(rows: list[LearnerRow]) -> str:
    lines = []
    for row in rows:
        flag = "!" if row.needs_attention else " "
        overdue = ",".join(row.overdue_modules) or "-"
        lines.append(f"{flag} {row.display_name:<18} {row.provider:<7} overdue={overdue}")
    return "\n".join(lines)
