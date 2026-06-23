from altvault.version import safe_version
from time import time
import httpx
import argparse

from altvault.github import create_github_client, GITHUB_OWNER
from altvault.recipes import recipes

LINE_SEPARATOR = "------------------------------------------------------------------------------------------"


def register(subparsers: argparse._SubParsersAction):
    parser = subparsers.add_parser("outdated")
    return parser


def run(_args: argparse.Namespace):
    app_list = recipes.items()
    outdated_list = []

    decrypted_dict = check_upload(
        repos={name: app.files_repo for name, app in app_list}
    )
    tweaked_dict = check_upload(
        repos={name: app.tweaks[0].files_repo for name, app in app_list if app.tweaks}
    )
    for name, version in tweaked_dict.items():
        tweaked_dict[name] = version.split("_")[0]
    appstore_dict = check_appstore(
        bundle_identifiers={name: app.bundle_identifier for name, app in app_list}
    )

    print(LINE_SEPARATOR)
    print(
        f"{'name':<14}",
        f"{'appstore':<9}",
        f"{'decrypted':<9}",
        f"{'': <2}",
        f"{'tweaked':<9}",
        f"{'': <2}",
        f"{'link'}",
    )
    print(LINE_SEPARATOR)

    for name, app in app_list:
        decrypted_is_outdated = not app.skip_outdated_check and safe_version(
            appstore_dict[name]["version"]
        ) > safe_version(decrypted_dict[name])

        tweaked_is_outdated = (
            not app.skip_outdated_check
            and name in tweaked_dict
            and safe_version(appstore_dict[name]["version"])
            > safe_version(tweaked_dict[name])
        )

        print(
            f"{name:<14}",
            f"{appstore_dict[name]['version']:<9}",
            f"{decrypted_dict[name] or '':<9}",
            f"{'✓' if decrypted_is_outdated else '': <2}",
            f"{tweaked_dict[name]:<9}",
            f"{'✓' if tweaked_is_outdated else '': <2}",
            f"{appstore_dict[name]['url']}",
        )
        if decrypted_is_outdated:
            outdated_list.append(app)
        pass


def check_upload(repos: dict[str, str]):
    github_client = create_github_client()

    fragment = """
fragment ReleaseInfo on Repository {
  latestRelease {
    tag {
      name
    }
  }
}
"""
    queries = []
    for name, repo in repos.items():
        queries.append(
            f'{name}: repository(owner: "{GITHUB_OWNER}", name: "{repo}") {{ ...ReleaseInfo }}'
        )

    query = f"query {{ {' '.join(queries)} }}\n{fragment}"
    query_result = github_client.graphql.request(query)

    result = {
        name: (data.get("latestRelease") or {}).get("tag", {}).get("name", None)
        for name, data in query_result.items()
    }

    return result


def check_appstore(bundle_identifiers: dict[str, str]):
    print(
        f"https://itunes.apple.com/lookup?bundleId={','.join(bundle_identifiers.values())}&cacheBusting={time()}"
    )
    response = httpx.get(
        f"https://itunes.apple.com/lookup?bundleId={','.join(bundle_identifiers.values())}&cacheBusting={time()}"
    )
    data = response.json()
    results = {}
    for name, bundle_identifier in bundle_identifiers.items():
        result = {}
        info = next(
            (x for x in data["results"] if x["bundleId"] == bundle_identifier), None
        )
        if info is not None:
            result["version"] = info["version"]
            result["url"] = info["trackViewUrl"]
            results[name] = result

    return results
