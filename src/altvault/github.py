import json
from functools import cache
from pathlib import Path

from githubkit import ActionAuthStrategy, GitHub

_globals_path = Path(__file__).parents[2] / "globals.json"
_globals_json = json.loads(_globals_path.read_text())
GITHUB_OWNER = _globals_json["owner"]
THIS_REPO = _globals_json["this_repo"]


@cache
def create_github_client() -> GitHub:
    return GitHub(ActionAuthStrategy())


def upload_release_asset(
    github_client: GitHub,
    upload_url: str,
    file_path: Path,
    asset_name: str | None = None,
) -> None:
    with open(file_path, "rb") as f:
        github_client.request(
            "POST",
            upload_url.split("{?")[0],
            params={"name": asset_name or file_path.name},
            # httpx streams file-like bodies in chunks and sets Content-Length via fstat
            content=f,
            headers={"Content-Type": "application/octet-stream"},
        )
