import json
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from githubkit import GitHub

if TYPE_CHECKING:
    from altvault.recipe import Recipe, Tweak


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
    current_ipa_path: Path
    tweak_version_label: str
    step_results: list[StepResult] = field(default_factory=list)


@dataclass
class StepResult:
    name: Literal["custom_apollo", "cyan", "downloadipa", "ipapatch", "prebuilt"]
    data: list[FileInfo] = field(default_factory=list)


@dataclass
class FileInfo:
    path: Path
    url: str
    sha256: str
    extracted_files: list[Path] = field(default_factory=list)


def file_info_serializer(obj):
    if isinstance(obj, Path):
        return obj.name
    raise TypeError(f"Type {type(obj).__name__} not serializable")


def file_info_to_json(data: FileInfo) -> str:
    return json.dumps(asdict(data), default=file_info_serializer, indent=4)
