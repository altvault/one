from altvault.download.github import GitHubReleaseFile
from altvault.recipes.base import Recipe, Tweak
from altvault.steps.cyan import CyanStep
from altvault.steps.downloadipa import DownloadIpaStep
from altvault.steps.ipapatch import IpapatchStep
from altvault.steps.uploadipa import UploadIpaStep

recipe = Recipe(
    name="Instagram",
    bundle_identifier="com.burbn.instagram",
    telegram_bot="FastDecryptBot",
    tweaks=[
        Tweak(
            name="RyukGram",
            pipeline=[
                DownloadIpaStep(),
                CyanStep(
                    download_files=[
                        GitHubReleaseFile(
                            owner="faroukbmiled",
                            repo="RyukGram",
                            endswith="rootless.deb",
                            use_version=True,
                            extract_deb_file_list=["RyukGram.dylib", "RyukGram.bundle"],
                        )
                    ]
                ),
                IpapatchStep(),
                UploadIpaStep(),
            ],
        ),
        Tweak(
            name="SCInsta",
            pipeline=[
                DownloadIpaStep(),
                CyanStep(
                    download_files=[
                        GitHubReleaseFile(
                            owner="SoCuul",
                            repo="SCInsta",
                            endswith="rootful.deb",
                            use_version=True,
                        )
                    ]
                ),
                IpapatchStep(),
                UploadIpaStep(),
            ],
        ),
    ],
)
