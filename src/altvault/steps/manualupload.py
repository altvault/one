import hashlib
from dataclasses import dataclass
from pathlib import Path

import questionary

from altvault.steps.base import Context, FileInfo, Step, StepResult


@dataclass(frozen=True)
class ManualUploadStep(Step):
    def run(self, context: Context) -> None:

        file_path_input = questionary.path("IPA Path").ask()
        if file_path_input is None:
            raise ValueError
        file_path = Path(file_path_input).expanduser()

        url = questionary.path("URL").ask()
        if url is None:
            raise ValueError

        with open(file_path, "rb") as f:
            sha256 = hashlib.file_digest(f, "sha256")

        file_info = FileInfo(path=file_path, url=url, sha256=sha256.hexdigest())

        context.current_ipa_path = file_info.path
        context.step_results.append(StepResult(name="manualupload", data=[file_info]))
