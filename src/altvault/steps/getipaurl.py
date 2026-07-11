from dataclasses import dataclass

from altvault.github import GITHUB_OWNER
from altvault.steps.base import Context, FileInfo, Step, StepResult


@dataclass(frozen=True)
class GetIpaUrlStep(Step):
    owner: str = GITHUB_OWNER
    repo: str | None = None
    tag: str = "latest"
    startswith: str | None = None
    endswith: str = ".ipa"

    def run(self, context: Context) -> None:
        target_repo = self.repo or context.recipe.files_repo

        if self.tag == "latest":
            release = context.github_client.rest.repos.get_latest_release(
                owner=self.owner, repo=target_repo
            )
        else:
            release = context.github_client.rest.repos.get_release_by_tag(
                owner=self.owner, repo=target_repo, tag=self.tag
            )

        if not release:
            raise ValueError("Release not found")

        assets = release.parsed_data.assets

        asset_to_download = None

        if not self.startswith and not self.endswith:
            asset_to_download = assets[0]

        def match_item(name: str) -> bool:
            if self.startswith and not name.startswith(self.startswith):
                return False
            if self.endswith and not name.endswith(self.endswith):
                return False
            return True

        for asset in assets:
            if match_item(asset.name):
                asset_to_download = asset
                break

        if asset_to_download is None:
            raise FileNotFoundError("Asset not found")

        # Make a request to the asset API endpoint to get the redirect URL
        response = context.github_client.request(
            "GET",
            f"/repos/{self.owner}/{target_repo}/releases/assets/{asset_to_download.id}",
            headers={"Accept": "application/octet-stream"},
            follow_redirects=False,
        )

        if response.status_code in (301, 302):
            cdn_url = response.headers["Location"]
        elif response.status_code == 200:
            # If it didn't redirect, maybe githubkit followed it anyway or it's direct
            cdn_url = str(response.url)
        else:
            raise ValueError(f"Failed to get CDN URL, status: {response.status_code}")

        context.ipa_download_url = cdn_url

        # Store minimal FileInfo
        file_info = FileInfo(
            path=context.work_dir / asset_to_download.name,
            url=cdn_url,
            sha256="",  # We don't download it so we don't know the sha256
        )

        context.step_results.append(StepResult(name="getipaurl", data=[file_info]))
