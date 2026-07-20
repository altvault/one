import hashlib
import subprocess
from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

from altvault.steps.base import Context, FileInfo


@dataclass(frozen=True, kw_only=True)
class DownloadFile(ABC):
    use_version: bool = False
    extract_deb_file_list: list[str] = field(default_factory=list)

    @abstractmethod
    def download(self, context: Context) -> FileInfo: ...

    @staticmethod
    def stream_to_file(chunks: Iterable[bytes], file_path: Path) -> str:
        """Write chunks to file_path, returning the sha256 hex digest."""
        sha256 = hashlib.sha256()
        with open(file_path, "wb") as f:
            for chunk in chunks:
                f.write(chunk)
                sha256.update(chunk)
        return sha256.hexdigest()

    def extract_deb_files(self, context: Context, file_path: Path) -> list[Path]:
        extracted_files = []
        if len(self.extract_deb_file_list) > 0:
            extract_folder = context.work_dir / file_path.stem
            extract_folder.mkdir()
            subprocess.run(
                [
                    "dpkg-deb",
                    "-x",
                    str(file_path),
                    str(extract_folder),
                ],
                check=True,
            )
            for item_to_extract in self.extract_deb_file_list:
                found_item = next(
                    (f for f in extract_folder.rglob(item_to_extract)), None
                )
                if not found_item:
                    raise FileNotFoundError(
                        f"{item_to_extract} not found in {file_path.name}"
                    )
                extracted_files.append(found_item)
        return extracted_files
