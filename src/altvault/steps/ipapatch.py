import subprocess
from dataclasses import dataclass
from pathlib import Path

from altvault.steps.base import Context, Step, StepResult


@dataclass(frozen=True)
class IpapatchStep(Step):
    def run(self, context: Context) -> None:
        if not context.current_ipa_path:
            raise ValueError("current_ipa_path is not set; no input IPA")

        step_path: Path = context.work_dir / "ipapatch"
        step_path.mkdir()
        input_ipa_path: Path = context.current_ipa_path
        final_ipa_path: Path = step_path / "final.ipa"

        subprocess.run(
            [
                "ipapatch",
                "--input",
                input_ipa_path,
                "--output",
                final_ipa_path,
                "--noconfirm",
            ],
            check=True,
            cwd=step_path,
        )

        context.current_ipa_path = final_ipa_path
        context.step_results.append(StepResult(name="ipapatch"))
