from altvault.download.github import GitHubReleaseFile
from altvault.recipes.base import Recipe, Tweak
from altvault.steps.cyan import CyanStep
from altvault.steps.downloadipa import DownloadIpaStep
from altvault.steps.uploadipa import UploadIpaStep

recipe = Recipe(
    name="YouTubeMusic",
    bundle_identifier="com.google.ios.youtubemusic",
    telegram_bot="eeveedecrypterbot",
    tweaks=[
        Tweak(
            name="YTMusicUltimate",
            pipeline=[
                DownloadIpaStep(),
                CyanStep(
                    download_files=[
                        GitHubReleaseFile(
                            owner="dayanch96",
                            repo="YTMusicUltimate",
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
