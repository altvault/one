from altvault.steps.uploadipa import UploadIpaStep
from altvault.download.cydia import CydiaRepoFile
from altvault.download.github import GitHubReleaseFile
from altvault.github import GITHUB_OWNER
from altvault.recipes.base import Recipe, Tweak
from altvault.steps.cyan import CyanStep
from altvault.steps.downloadipa import DownloadIpaStep

recipe = Recipe(
    name="YouTube",
    bundle_identifier="com.google.ios.youtube",
    telegram_bot="eeveedecrypterbot",
    tweaks=[
        Tweak(
            name="MyYouTube",
            pipeline=[
                DownloadIpaStep(),
                CyanStep(
                    download_files=[
                        CydiaRepoFile(
                            repo="https://poomsmart.github.io/repo",
                            package="com.ps.ytabgoodies",
                            architecture="iphoneos-arm",
                        ),
                        CydiaRepoFile(
                            repo="https://poomsmart.github.io/repo",
                            package="com.ps.ytx",
                            architecture="iphoneos-arm",
                        ),
                        CydiaRepoFile(
                            repo="https://poomsmart.github.io/repo",
                            package="com.ps.ytvideooverlay",
                            architecture="iphoneos-arm",
                        ),
                        CydiaRepoFile(
                            repo="https://poomsmart.github.io/repo",
                            package="com.ps.youpip",
                            architecture="iphoneos-arm",
                        ),
                        GitHubReleaseFile(
                            owner="hbang",
                            repo="Alderis",
                            tag="1.2.3",
                            endswith="arm.deb",
                        ),
                        CydiaRepoFile(
                            repo="https://repo.icrazeios.com",
                            package="com.galacticdev.isponsorblock",
                            architecture="iphoneos-arm",
                        ),
                        GitHubReleaseFile(
                            owner=GITHUB_OWNER,
                            repo="YTStartupTab",
                            endswith="arm.deb",
                        ),
                        GitHubReleaseFile(
                            owner="Balackburn",
                            repo="YTSideload",
                            endswith="YTSideload.dylib",
                        ),
                        # GitHubReleaseFile(
                        #     owner="arichornlover",
                        #     repo="YTAppVersionSpoofer",
                        #     endswith="arm.deb",
                        # ),
                    ]
                ),
                UploadIpaStep(),
            ],
        ),
        Tweak(
            name="YouMod",
            pipeline=[
                DownloadIpaStep(),
                CyanStep(
                    download_files=[
                        GitHubReleaseFile(
                            owner="Tonwalter888",
                            repo="YouMod",
                            endswith="arm.deb",
                            use_version=True,
                        ),
                        CydiaRepoFile(
                            repo="https://poomsmart.github.io/repo",
                            package="com.ps.ytvideooverlay",
                            architecture="iphoneos-arm",
                        ),
                        CydiaRepoFile(
                            repo="https://poomsmart.github.io/repo",
                            package="com.ps.youpip",
                            architecture="iphoneos-arm",
                        ),
                    ]
                ),
                UploadIpaStep(),
            ],
        ),
    ],
)
