from dataclasses import dataclass

from altvault.download.base import DownloadFile
from altvault.steps.base import Context, Step, StepResult


@dataclass(frozen=True)
class PrebuiltStep(Step):
    download_file: DownloadFile

    def run(self, context: Context) -> None:
        file_info = self.download_file.download(context)

        context.current_ipa_path = file_info.path
        context.step_results.append(StepResult(name="prebuilt", data=[file_info]))
