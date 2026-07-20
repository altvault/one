import datetime as dt
import json
from dataclasses import dataclass
from zoneinfo import ZoneInfo

from altvault.github import GITHUB_OWNER, upload_release_asset
from altvault.ipa import extract_ipa_metadata
from altvault.steps.base import Context, Step


@dataclass(frozen=True)
class UploadIpaStep(Step):
    def run(self, context: Context) -> None:
        if not context.current_ipa_path:
            raise ValueError("current_ipa_path is not set; nothing to upload")
        if not context.app_version or context.app_version == "latest":
            context.app_version = extract_ipa_metadata(context.current_ipa_path).version
        if not context.tweak_version_label:
            context.tweak_version_label = dt.datetime.now(
                ZoneInfo("Asia/Bangkok")
            ).strftime("%Y%m%d%H%M")
        file_name = f"{context.recipe.name}_{context.app_version}_{context.tweak.name}_{context.tweak_version_label}.ipa"
        release_tag = f"{context.app_version}_{context.tweak_version_label}"
        body_json = json.dumps(
            {
                "name": context.recipe.name,
                "bundleIdentifier": context.recipe.bundle_identifier,
                "step_results": [r.to_dict() for r in context.step_results],
            },
            indent=4,
        )
        release_body = f"```json\n{body_json}\n```"
        release = context.github_client.rest.repos.create_release(
            owner=GITHUB_OWNER,
            repo=context.tweak.files_repo,
            tag_name=release_tag,
            body=release_body,
        )
        upload_release_asset(
            context.github_client,
            release.parsed_data.upload_url,
            context.current_ipa_path,
            asset_name=file_name,
        )

        for step_result in context.step_results:
            if step_result.name == "cyan":
                for file_info in step_result.data:
                    upload_release_asset(
                        context.github_client,
                        release.parsed_data.upload_url,
                        file_info.path,
                    )
