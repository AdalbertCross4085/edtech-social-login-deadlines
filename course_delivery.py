"""Course delivery model: sessions, learner enrolment and deadline schedule."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Literal

Provider = Literal["google", "github"]


@dataclass(frozen=True)
class Module:
    slug: str
    title: str
    day_offset: int          # days after enrolment the module unlocks
    grace_days: int = 3      # extra days a learner has to submit


@dataclass(frozen=True)
class Course:
    code: str
    title: str
    modules: tuple[Module, ...]


@dataclass(frozen=True)
class Learner:
    email: str
    display_name: str
    provider: Provider
    provider_account_id: str

    @property
    def learner_id(self) -> str:
        return f"{self.provider}:{self.provider_account_id}"


@dataclass(frozen=True)
class Deadline:
    module_slug: str
    unlocks_on: date
    due_on: date


@dataclass
class Enrolment:
    learner: Learner
    course: Course
    started_on: date
    deadlines: list[Deadline] = field(default_factory=list)


CS_INTRO = Course(
    code="CS-101",
    title="Introduction to Backend Services",
    modules=(
        Module("http-basics", "HTTP and status codes", day_offset=0),
        Module("auth-flows", "OAuth callbacks end to end", day_offset=7),
        Module("data-modelling", "Modelling deadlines", day_offset=14, grace_days=5),
    ),
)


def build_schedule(course: Course, started_on: date) -> list[Deadline]:
    return [
        Deadline(
            module_slug=module.slug,
            unlocks_on=started_on + timedelta(days=module.day_offset),
            due_on=started_on + timedelta(days=module.day_offset + 7 + module.grace_days),
        )
        for module in course.modules
    ]


def enrol(learner: Learner, course: Course, started_on: date) -> Enrolment:
    return Enrolment(
        learner=learner,
        course=course,
        started_on=started_on,
        deadlines=build_schedule(course, started_on),
    )


def module_state(deadline: Deadline, today: date) -> str:
    if today < deadline.unlocks_on:
        return "locked"
    if today <= deadline.due_on:
        return "open"
    return "overdue"
