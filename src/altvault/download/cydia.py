import gzip
from dataclasses import dataclass
from os.path import basename
from urllib.parse import urljoin, urlparse

import httpx
from debian.deb822 import Packages

from altvault.download.base import DownloadFile
from altvault.steps.base import Context, FileInfo
from altvault.version import safe_version


def _fetch_cydia_repo(url: str) -> list[Packages]:
    packages_gz_url = f"{url}/Packages.gz"
    response = httpx.get(packages_gz_url)
    content = gzip.decompress(response.content).decode("utf-8")
    packages = list(Packages.iter_paragraphs(content, use_apt_pkg=False))
    return packages


@dataclass(frozen=True)
class CydiaRepoFile(DownloadFile):
    repo: str
    package: str
    architecture: str
    version: str = "latest"

    def download(self, context: Context) -> FileInfo:
        all_packages = _fetch_cydia_repo(self.repo)
        filtered_packages = [
            pkg
            for pkg in all_packages
            if pkg["Package"] == self.package
            and pkg["Architecture"] == self.architecture
        ]
        if self.version == "latest":
            selected_package = max(
                filtered_packages, key=lambda p: safe_version(p["Version"])
            )
        else:
            selected_package = next(
                (p for p in filtered_packages if p["Version"] == self.version), None
            )
        if not selected_package:
            raise ValueError("Not found")
        if self.use_version:
            context.tweak_version_label = selected_package["Version"]

        download_url = urljoin(f"{self.repo}/", selected_package["Filename"])

        with httpx.stream("GET", download_url, follow_redirects=True) as r:
            r.raise_for_status()
            file_path = context.work_dir / basename(urlparse(download_url).path)
            sha256 = self.stream_to_file(r.iter_bytes(), file_path)

        extracted_files = self.extract_deb_files(context, file_path)

        return FileInfo(
            path=file_path,
            url=download_url,
            sha256=sha256,
            extracted_files=extracted_files,
        )
