import argparse
import subprocess

import questionary

from altvault.github import GITHUB_OWNER, THIS_REPO, create_github_client
from altvault.recipes import recipes


def register(subparsers: argparse._SubParsersAction):
    parser = subparsers.add_parser("dispatch")
    parser.add_argument("tweak_name", nargs="?")
    parser.add_argument("--app-version")
    return parser


def run(args: argparse.Namespace):
    tweak_name = args.tweak_name
    app_version = args.app_version

    if not tweak_name:
        all_tweaks = sorted([t.name for r in recipes.values() for t in r.tweaks])
        tweak_name = questionary.autocomplete("tweak_name:", choices=all_tweaks).ask()

    if not app_version:
        app_version = questionary.text("app_version:", default="latest").ask()

    if not tweak_name or not app_version:
        raise ValueError

    if questionary.confirm(f"Dispatch pipeline for {tweak_name} {app_version}").ask():
        github_client = create_github_client()

        result = github_client.rest.actions.create_workflow_dispatch(
            owner=GITHUB_OWNER,
            repo=THIS_REPO,
            workflow_id="pipeline.yml",
            data={
                "ref": "main",
                "inputs": {
                    "tweak_name": tweak_name,
                    "app_version": app_version,
                },
            },
        )

        print("Workflow dispatched", result.parsed_data.html_url)
        print()

        if result.parsed_data.workflow_run_id:
            subprocess.run(
                [
                    "gh",
                    "run",
                    "watch",
                    "--repo",
                    f"{GITHUB_OWNER}/{THIS_REPO}",
                    str(result.parsed_data.workflow_run_id),
                ]
            )
    else:
        print("Aborted.")
