from altvault.download.github import GitHubReleaseFile
from altvault.recipes.base import Recipe, Tweak
from altvault.steps.cyan import CyanStep
from altvault.steps.downloadipa import DownloadIpaStep
from altvault.steps.uploadipa import UploadIpaStep

recipe = Recipe(
    name="Infuse",
    bundle_identifier="com.firecore.infuse",
    telegram_bot="eeveedecrypterbot",
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
                UploadIpaStep(),
            ],
        )
    ],
)
