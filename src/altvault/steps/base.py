from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from githubkit import GitHub

if TYPE_CHECKING:
    from altvault.recipes.base import Recipe, Tweak


@dataclass(frozen=True)
class Step(ABC):
    @abstractmethod
    def run(self, context: Context) -> None: ...


@dataclass
class Context:
    recipe: Recipe
    tweak: Tweak
    app_version: str
    github_client: GitHub
    work_dir: Path
    current_ipa_path: Path | None = None
    tweak_version_label: str | None = None
    step_results: list[StepResult] = field(default_factory=list)


@dataclass
class StepResult:
    name: Literal["cyan", "downloadipa", "ipapatch", "prebuilt", "manualupload"]
    data: list[FileInfo] = field(default_factory=list)

    def to_dict(self):
        return {"name": self.name, "data": [x.to_dict() for x in self.data]}


@dataclass
class FileInfo:
    path: Path
    url: str
    sha256: str
    extracted_files: list[Path] = field(default_factory=list)

    def to_dict(self):
        return {
            "path": self.path.name,
            "url": self.url,
            "sha256": self.sha256,
            "extracted_files": [x.name for x in self.extracted_files],
        }
