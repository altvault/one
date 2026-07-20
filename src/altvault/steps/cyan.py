from pathlib import Path
from dataclasses import dataclass, field
import subprocess

from altvault.download.base import DownloadFile
from altvault.steps.base import Context, Step, StepResult


@dataclass(frozen=True)
class CyanStep(Step):
    download_files: list[DownloadFile] = field(default_factory=list)

    def run(self, context: Context) -> None:
        if not context.current_ipa_path:
            raise ValueError("current_ipa_path is not set; no input IPA")
        file_infos = [file.download(context) for file in self.download_files]

        step_path: Path = context.work_dir / "cyan"
        step_path.mkdir()
        input_ipa_path: Path = context.current_ipa_path
        final_ipa_path: Path = step_path / "final.ipa"
        files_to_inject: list[Path] = []
        for file_info in file_infos:
            if (len(file_info.extracted_files)) > 0:
                files_to_inject.extend(file_info.extracted_files)
            else:
                files_to_inject.append(file_info.path)

        subprocess.run(
            [
                "cyan",
                "--input",
                input_ipa_path,
                "--output",
                final_ipa_path,
                # "--remove-supported-devices",
                # "--no-watch",
                # "--remove-encrypted",
                "-f",
                *files_to_inject,
            ],
            check=True,
            cwd=step_path,
        )

        context.current_ipa_path = final_ipa_path
        context.step_results.append(StepResult(name="cyan", data=file_infos))
