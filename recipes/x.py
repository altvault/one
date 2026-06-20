from altvault.download.github import GitHubReleaseFile
from altvault.recipe import Recipe, Tweak
from altvault.steps.cyan import CyanStep
from altvault.steps.downloadipa import DownloadIpaStep

recipe = Recipe(
    name="X",
    bundle_identifier="com.atebits.Tweetie2",
    tweaks=[
        Tweak(
            name="BHTwitter",
            pipeline=[
                DownloadIpaStep(),
                CyanStep(
                    download_files=[
                        GitHubReleaseFile(
                            owner="BandarHL",
                            repo="BHTwitter",
                            endswith="arm.deb",
                            use_version=True,
                        )
                    ]
                ),
            ],
        )
    ],
)
