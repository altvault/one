from altvault.download.github import GitHubReleaseFile
from altvault.recipes.base import Recipe, Tweak
from altvault.steps.cyan import CyanStep
from altvault.steps.downloadipa import DownloadIpaStep

recipe = Recipe(
    name="Infuse",
    bundle_identifier="com.firecore.infuse",
    tweaks=[
        Tweak(
            name="InfusePlus",
            pipeline=[
                DownloadIpaStep(),
                CyanStep(
                    download_files=[
                        GitHubReleaseFile(
                            owner="dayanch96",
                            repo="InfusePlus",
                            endswith="arm.deb",
                            use_version=True,
                        )
                    ]
                ),
            ],
        )
    ],
)
