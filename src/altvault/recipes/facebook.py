from altvault.download.github import GitHubReleaseFile
from altvault.recipes.base import Recipe, Tweak
from altvault.steps.cyan import CyanStep
from altvault.steps.downloadipa import DownloadIpaStep

recipe = Recipe(
    name="Facebook",
    bundle_identifier="com.facebook.Facebook",
    telegram_bot="eeveedecrypterbot",
    tweaks=[
        Tweak(
            name="FacebookGlow",
            pipeline=[
                DownloadIpaStep(),
                CyanStep(
                    download_files=[
                        GitHubReleaseFile(
                            owner="dayanch96",
                            repo="Glow",
                            endswith="arm.deb",
                            use_version=True,
                        )
                    ]
                ),
            ],
        )
    ],
)
