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
