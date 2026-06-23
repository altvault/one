import argparse
import asyncio
import subprocess
from dataclasses import dataclass
from time import time
from typing import Literal, NamedTuple

import httpx
import questionary
from githubkit import GitHub
from githubkit.exception import RequestFailed
from githubkit_schemas.latest.models import MinimalRepository

from altvault.github import GITHUB_OWNER, create_github_client
from altvault.recipes import recipes
from altvault.version import safe_version

DASH_SEPARATOR = "-" * 90
CONCURRENCY_LIMIT: int = 15


def register(subparsers: argparse._SubParsersAction):
    parser = subparsers.add_parser("outdated")
    return parser


def run(_args: argparse.Namespace):
    asyncio.run(arun())


async def arun():
    sem = asyncio.Semaphore(CONCURRENCY_LIMIT)
    github_client = create_github_client()
    await check_forks(github_client=github_client, sem=sem)
    print()
    await check_versions(github_client=github_client, sem=sem)
    print()


# region Forks


class CheckForkBehindResult(NamedTuple):
    url: str
    status: Literal["diverged", "ahead", "behind", "identical"]
    behind_by: int


async def check_forks(github_client: GitHub, sem: asyncio.Semaphore):
    async with sem:
        forks = [
            repo
            async for repo in github_client.rest.paginate(
                github_client.rest.repos.async_list_for_org,
                org=GITHUB_OWNER,
                type="forks",
                per_page=100,
            )
        ]
    tasks = [
        check_fork_behind(minimal_repo=repo, github_client=github_client, sem=sem)
        for repo in forks
    ]
    diff_repos: list[CheckForkBehindResult] = []
    completed: int = 0
    total: int = len(tasks)
    print()
    for task in asyncio.as_completed(tasks):
        result = await task
        if result and result.status != "identical":
            diff_repos.append(result)
        completed += 1
        print(f"\rForks: Checking {completed:>2}/{total}", end="", flush=True)
    print()
    print()
    if diff_repos:
        for item in diff_repos:
            questionary.print(
                f"{item.status} {item.behind_by} {item.url}", style="yellow"
            )
    else:
        questionary.print("all identical", style="green")


async def check_fork_behind(
    minimal_repo: MinimalRepository, github_client: GitHub, sem: asyncio.Semaphore
) -> CheckForkBehindResult | None:
    async with sem:
        repo = (
            await github_client.rest.repos.async_get(
                owner=minimal_repo.owner.login, repo=minimal_repo.name
            )
        ).parsed_data
        parent = repo.parent
        if parent and parent.owner:
            base = f"{parent.owner.login}:{parent.default_branch}"
            head = f"{repo.owner.login}:{repo.default_branch}"
            compared = (
                await github_client.rest.repos.async_compare_commits(
                    owner=repo.owner.login, repo=repo.name, basehead=f"{base}...{head}"
                )
            ).parsed_data
            return CheckForkBehindResult(
                url=repo.html_url,
                status=compared.status,
                behind_by=compared.behind_by,
            )


# endregion

# region Versions


@dataclass
class CheckVersionResult:
    name: str
    appstore_url: str | None = None
    appstore_version: str | None = None
    decrypted_version: str | None = None
    decrypted_outdated: bool | None = None
    tweaked_version: str | None = None
    tweaked_outdated: bool | None = None


type CheckVersionResultDict = dict[str, CheckVersionResult]


async def check_versions(github_client: GitHub, sem: asyncio.Semaphore):
    results: CheckVersionResultDict = {
        name: CheckVersionResult(name=name) for name in recipes
    }
    tasks = []
    async with httpx.AsyncClient() as client:
        for name, app in recipes.items():
            tasks.append(
                get_our_version(
                    version_of="decrypted",
                    name=name,
                    repo=app.files_repo,
                    results=results,
                    github_client=github_client,
                    sem=sem,
                )
            )
            tasks.append(
                get_appstore_version(
                    name=name,
                    bundle_identifier=app.bundle_identifier,
                    results=results,
                    client=client,
                )
            )
            if len(app.tweaks) > 0:
                tasks.append(
                    get_our_version(
                        version_of="tweaked",
                        name=name,
                        repo=app.tweaks[0].files_repo,
                        results=results,
                        github_client=github_client,
                        sem=sem,
                    )
                )

        completed: int = 0
        total: int = len(tasks)
        print()
        for task in asyncio.as_completed(tasks):
            await task
            completed += 1
            print(f"\rApps: Checking {completed:>2}/{total}", end="", flush=True)
    print()
    print()
    print(
        f"{'name':<14}",
        f"{'appstore':<9}",
        f"{'decrypted':<9}",
        f"{'': <2}",
        f"{'tweaked':<9}",
        f"{'': <2}",
        f"{'link'}",
    )
    print(DASH_SEPARATOR)
    outdated_list: list[CheckVersionResult] = []
    for name, app in recipes.items():
        result = results[name]
        if result.appstore_version and result.decrypted_version:
            result.decrypted_outdated = not app.skip_outdated_check and safe_version(
                result.appstore_version
            ) > safe_version(result.decrypted_version)
            if result.decrypted_outdated:
                outdated_list.append(result)
        if result.appstore_version and result.tweaked_version:
            result.tweaked_outdated = not app.skip_outdated_check and safe_version(
                result.appstore_version
            ) > safe_version(result.tweaked_version)
        print(
            f"{result.name:<14}",
            f"{result.appstore_version:<9}",
            f"{result.decrypted_version or '':<9}",
            f"{'✓' if result.decrypted_outdated else '': <2}",
            f"{result.tweaked_version or '':<9}",
            f"{'✓' if result.tweaked_outdated else '': <2}",
            f"{result.appstore_url}",
        )

    if len(outdated_list) > 0:
        print()
        for outdated_result in outdated_list:
            if await questionary.confirm(
                f"Update {outdated_result.name} {outdated_result.decrypted_version} -> {outdated_result.appstore_version}",
                default=True,
            ).ask_async():
                telegram_link = f"tg://resolve?domain={recipes[outdated_result.name].telegram_bot}&text={outdated_result.appstore_url}"
                subprocess.run(["open", telegram_link], check=True)


async def get_our_version(
    version_of: Literal["decrypted", "tweaked"],
    name: str,
    repo: str,
    results: CheckVersionResultDict,
    github_client: GitHub,
    sem: asyncio.Semaphore,
):
    async with sem:
        try:
            release = await github_client.rest.repos.async_get_latest_release(
                owner=GITHUB_OWNER,
                repo=repo,
            )
            if version_of == "decrypted":
                results[name].decrypted_version = release.parsed_data.tag_name
            elif version_of == "tweaked":
                results[name].tweaked_version = release.parsed_data.tag_name.split("_")[
                    0
                ]

        except RequestFailed as e:
            if e.response.status_code == 404:
                return None
            else:
                raise


async def get_appstore_version(
    name: str,
    bundle_identifier: str,
    results: CheckVersionResultDict,
    client: httpx.AsyncClient,
):
    response = await client.get(
        f"https://itunes.apple.com/lookup?bundleId={bundle_identifier}&cacheBusting={time()}"
    )
    data = response.json()
    results[name].appstore_version = data["results"][0]["version"]
    results[name].appstore_url = data["results"][0]["trackViewUrl"]


# endregion
