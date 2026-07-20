import argparse
import subprocess
from pathlib import Path

import questionary
from githubkit.exception import RequestFailed

from altvault.github import GITHUB_OWNER, create_github_client, upload_release_asset
from altvault.ipa import extract_ipa_metadata
from altvault.recipes import get_recipe
from altvault.version import safe_version

DEFAULT_FOLDER = "~/Downloads/Telegram Desktop/"


def register(subparsers: argparse._SubParsersAction):
    parser = subparsers.add_parser("upload")
    parser.add_argument("ipa_path", nargs="?")
    parser.add_argument("--note")
    return parser


def ipa_path_filter(path_str: str):
    p = Path(path_str)
    return p.is_dir() or p.suffix.lower() == ".ipa"


def run(args: argparse.Namespace):
    github_client = create_github_client()

    ipa_path_input: str | None = args.ipa_path
    if ipa_path_input is None:
        ipa_path_input = questionary.path(
            "IPA Path",
            default=DEFAULT_FOLDER,
            file_filter=ipa_path_filter,
        ).ask()

    if ipa_path_input is None:
        raise ValueError

    ipa_path = Path(ipa_path_input).expanduser()

    if not ipa_path.is_file():
        raise ValueError

    ipa_filename = ipa_path.name

    metadata = extract_ipa_metadata(ipa_path)

    recipe = get_recipe(bundle_identifier=metadata.bundle_identifier)

    notes = ""
    if "-eeveedecrypter" in ipa_filename:
        notes += "eeveedecrypter"
    elif "-Decrypted" in ipa_filename:
        notes += "armconverter"
    elif "_decrypt_" in ipa_filename:
        notes += "anyipa"
    elif "-AppAssassin" in ipa_filename:
        notes += "appassassin"

    if args.note:
        notes += args.note if notes == "" else f"\n{args.note}"

    # check latest
    try:
        latest = github_client.rest.repos.get_latest_release(
            owner=GITHUB_OWNER,
            repo=recipe.files_repo,
        )
        newer = safe_version(metadata.version) > safe_version(
            latest.parsed_data.tag_name
        )
    except RequestFailed as e:
        if e.response.status_code == 404:
            newer = True
        else:
            raise

    print("=======================")
    print(f"File Name: {ipa_filename}")
    print(f"Notes: {notes}")
    print(f"Newer: {newer}")
    print()

    if questionary.confirm("Upload?", default=True).ask():
        # create release
        release = github_client.rest.repos.create_release(
            owner=GITHUB_OWNER,
            repo=recipe.files_repo,
            tag_name=metadata.version,
            body=notes,
            make_latest="true" if newer else "false",
        )

        # upload
        upload_release_asset(
            github_client,
            release.parsed_data.upload_url,
            ipa_path,
            asset_name=ipa_filename,
        )

        if questionary.confirm("Delete file?", default=True).ask():
            subprocess.run(["trash", ipa_path])

            default_folder = Path(DEFAULT_FOLDER).expanduser()
            # if ipa path is in the telegram downloads folder
            if ipa_path.is_relative_to(default_folder):
                # if telegram downloads folder is empty
                if default_folder.is_dir() and not any(default_folder.iterdir()):
                    if questionary.confirm("Delete folder?", default=True).ask():
                        subprocess.run(["trash", default_folder])
