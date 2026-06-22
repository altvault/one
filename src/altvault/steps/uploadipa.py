import json
from dataclasses import dataclass

from altvault.github import GITHUB_OWNER
from altvault.steps.base import Context, Step


@dataclass(frozen=True)
class UploadIpaStep(Step):
    def run(self, context: Context) -> None:
        file_name = f"{context.recipe.name}_{context.app_version}_{context.tweak.name}_{context.tweak_version_label}"
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
        with open(context.current_ipa_path, "rb") as f:
            context.github_client.request(
                "POST",
                release.parsed_data.upload_url.split("{?")[0],
                params={"name": file_name},
                content=f.read(),
                headers={"Content-Type": "application/octet-stream"},
            )
