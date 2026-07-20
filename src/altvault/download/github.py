from dataclasses import dataclass

from altvault.download.base import DownloadFile
from altvault.steps.base import Context, FileInfo


@dataclass(frozen=True)
class GitHubReleaseFile(DownloadFile):
    owner: str
    repo: str
    tag: str = "latest"
    startswith: str | None = None
    endswith: str | None = None

    def download(self, context: Context) -> FileInfo:
        if self.tag == "latest":
            release = context.github_client.rest.repos.get_latest_release(
                owner=self.owner, repo=self.repo
            )
        else:
            release = context.github_client.rest.repos.get_release_by_tag(
                owner=self.owner, repo=self.repo, tag=self.tag
            )
        if not release:
            raise ValueError("Release not found")
        assets = release.parsed_data.assets
        if self.use_version:
            tag_name = release.parsed_data.tag_name.removeprefix("v")
            context.tweak_version_label = tag_name

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
            raise FileNotFoundError(
                f"No matching asset in {self.owner}/{self.repo}@{self.tag} "
                f"(startswith={self.startswith!r}, endswith={self.endswith!r})"
            )

        download_asset = context.github_client.rest.repos.get_release_asset(
            owner=self.owner,
            repo=self.repo,
            asset_id=asset_to_download.id,
            headers={"Accept": "application/octet-stream"},
        )
        file_path = context.work_dir / asset_to_download.name
        sha256 = self.stream_to_file(download_asset.iter_bytes(), file_path)

        extracted_files = self.extract_deb_files(context, file_path)

        return FileInfo(
            path=file_path,
            url=asset_to_download.browser_download_url,
            sha256=sha256,
            extracted_files=extracted_files,
        )
