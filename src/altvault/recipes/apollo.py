from dataclasses import dataclass

from altvault.download.github import GitHubReleaseFile
from altvault.recipes.base import Recipe, Tweak
from altvault.steps.base import Context, Step
from altvault.steps.prebuilt import PrebuiltStep


@dataclass(frozen=True)
class ApolloRebornTrimVersionStep(Step):
    def run(self, context: Context) -> None:
        if context.tweak_version_label:
            version_parts = context.tweak_version_label.removeprefix("v").split("_")
            context.tweak_version_label = version_parts[1]


recipe = Recipe(
    name="Apollo",
    bundle_identifier="com.christianselig.Apollo",
    skip_outdated_check=True,
    telegram_bot="eeveedecrypterbot",
    tweaks=[
        Tweak(
            name="ApolloReborn",
            pipeline=[
                PrebuiltStep(
                    download_file=GitHubReleaseFile(
                        owner="Apollo-Reborn",
                        repo="Apollo-Reborn",
                        endswith="-GLASS.ipa",
                        use_version=True,
                    )
                ),
                ApolloRebornTrimVersionStep(),
            ],
            # pipeline=[
            #     DownloadIpaStep(),
            #     CyanStep(
            #         download_files=[
            #             GitHubReleaseFile(
            #                 owner="Apollo-Reborn",
            #                 repo="Apollo-Reborn",
            #                 endswith="arm.deb",
            #                 use_version=True,
            #             )
            #         ]
            #     ),
            #     CustomApolloStep()
            # ],
        )
    ],
)
