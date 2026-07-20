import argparse
import re
from pathlib import Path

from altvault.recipes import get_ci_tweak_names

WORKFLOW_PATH = Path(__file__).parents[3] / ".github" / "workflows" / "pipeline.yml"
# the "options:" block under tweak_name and its "- Name" lines
OPTIONS_RE = re.compile(r"(^        options:\n)((?:^          - .+\n)+)", re.MULTILINE)


def register(subparsers: argparse._SubParsersAction):
    parser = subparsers.add_parser("sync-workflow")
    parser.add_argument("--check", action="store_true")
    return parser


def run(args: argparse.Namespace):
    text = WORKFLOW_PATH.read_text()
    options = "".join(f"          - {name}\n" for name in get_ci_tweak_names())
    new_text, count = OPTIONS_RE.subn(lambda m: m.group(1) + options, text, count=1)
    if count != 1:
        raise ValueError(f"options block not found in {WORKFLOW_PATH}")
    if new_text == text:
        print("pipeline.yml tweak options are in sync")
        return
    if args.check:
        raise SystemExit(
            "pipeline.yml tweak options are out of sync; run: uv run altvault sync-workflow"
        )
    WORKFLOW_PATH.write_text(new_text)
    print("pipeline.yml updated")
