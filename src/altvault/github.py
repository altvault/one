import json
from functools import cache
from pathlib import Path

from githubkit import ActionAuthStrategy, GitHub

_globals = Path(__file__).parents[2] / "globals.json"
GITHUB_OWNER = json.loads(_globals.read_text())["owner"]


@cache
def create_github_client() -> GitHub:
    return GitHub(ActionAuthStrategy())
