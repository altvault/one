from altvault.download.github import GitHubReleaseFile
from altvault.recipes.base import Recipe, Tweak
from altvault.steps.cyan import CyanStep
from altvault.steps.downloadipa import DownloadIpaStep
from altvault.steps.ipapatch import IpapatchStep
from altvault.steps.manualupload import ManualUploadStep
from altvault.steps.uploadipa import UploadIpaStep

recipe = Recipe(
    name="X",
    bundle_identifier="com.atebits.Tweetie2",
    telegram_bot="FastDecryptBot",
    tweaks=[
        Tweak(
            name="TheacratNFB",
            pipeline=[
                DownloadIpaStep(),
                CyanStep(
                    download_files=[
                        GitHubReleaseFile(
                            owner="theacrat",
                            repo="NeoFreeBird",
                            endswith="arm.deb",
                            use_version=True,
                        )
                    ]
                ),
                IpapatchStep(),
                UploadIpaStep(),
            ],
        ),
        Tweak(name="DLTwitter", pipeline=[ManualUploadStep(), UploadIpaStep()]),
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
                UploadIpaStep(),
            ],
        ),
    ],
)
