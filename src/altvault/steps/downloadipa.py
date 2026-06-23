from altvault.ipa import extract_ipa_metadata
from dataclasses import dataclass

from altvault.download.github import GitHubReleaseFile
from altvault.github import GITHUB_OWNER
from altvault.steps.base import Context, Step, StepResult


@dataclass(frozen=True)
class DownloadIpaStep(Step):
    def run(self, context: Context) -> None:
        downloader = GitHubReleaseFile(
            owner=GITHUB_OWNER,
            repo=context.recipe.files_repo,
            tag=context.app_version,
            endswith=".ipa",
        )
        file_info = downloader.download(context)

        if context.app_version == "latest":
            context.app_version = extract_ipa_metadata(file_info.path).version
        context.current_ipa_path = file_info.path
        context.step_results.append(StepResult(name="downloadipa", data=[file_info]))
