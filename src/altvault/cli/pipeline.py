import argparse
import tempfile
from pathlib import Path

from altvault.github import create_github_client
from altvault.recipes import get_tweak_recipe
from altvault.steps.base import Context


def register(subparsers: argparse._SubParsersAction):
    parser = subparsers.add_parser("pipeline")
    parser.add_argument("tweak_name")
    parser.add_argument("--app-version")
    return parser


def run(args: argparse.Namespace):
    github_client = create_github_client()
    recipe = get_tweak_recipe(name=args.tweak_name)

    with tempfile.TemporaryDirectory() as tmpdirname:
        tmpdir: Path = Path(tmpdirname)
        context: Context = Context(
            recipe=recipe.app,
            tweak=recipe.tweak,
            app_version=args.app_version,
            github_client=github_client,
            work_dir=tmpdir,
        )

        for step in recipe.tweak.pipeline:
            print("Step:", type(step).__name__)
            step.run(context=context)
