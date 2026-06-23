from dataclasses import dataclass, field

from altvault.steps.base import Step


@dataclass(frozen=True)
class Recipe:
    name: str
    bundle_identifier: str
    skip_outdated_check: bool = False
    telegram_bot: str | None = None
    tweaks: list[Tweak] = field(default_factory=list)

    @property
    def files_repo(self) -> str:
        return f"{self.name}-files"


@dataclass(frozen=True)
class Tweak:
    name: str
    note: str | None = None
    pipeline: list[Step] = field(default_factory=list)

    @property
    def files_repo(self) -> str:
        return f"{self.name}-files"
