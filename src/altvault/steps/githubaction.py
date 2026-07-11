import datetime
import hashlib
import time
from dataclasses import dataclass, field

from altvault.steps.base import Context, FileInfo, Step, StepResult


@dataclass(frozen=True)
class GithubActionStep(Step):
    owner: str
    repo: str
    workflow_id: str
    ipa_url_input: str
    ref: str = "main"
    extra_inputs: dict[str, str] = field(default_factory=dict)
    
    # We poll for the workflow to finish, we need timeouts
    find_run_timeout_seconds: int = 60
    run_timeout_seconds: int = 3600

    def run(self, context: Context) -> None:
        if not context.ipa_download_url:
            raise ValueError("context.ipa_download_url is required for GithubActionStep")

        inputs = {self.ipa_url_input: context.ipa_download_url}
        inputs.update(self.extra_inputs)

        start_time = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
        start_time_iso = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")

        # 1. Trigger workflow
        context.github_client.rest.actions.create_workflow_dispatch(
            owner=self.owner,
            repo=self.repo,
            workflow_id=self.workflow_id,
            data={"ref": self.ref, "inputs": inputs},
        )

        # 2. Wait for workflow run to appear
        run = None
        started_waiting = time.time()
        while time.time() - started_waiting < self.find_run_timeout_seconds:
            runs_response = context.github_client.rest.actions.list_workflow_runs(
                owner=self.owner,
                repo=self.repo,
                workflow_id=self.workflow_id,
                event="workflow_dispatch",
                created=f">={start_time_iso}",
            )
            runs = runs_response.parsed_data.workflow_runs
            # find runs created by this user
            if runs:
                # We assume the first one is ours since we just dispatched it
                # Sort by created_at desc to get the most recent one
                runs.sort(key=lambda r: r.created_at, reverse=True)
                run = runs[0]
                break
            time.sleep(5)

        if not run:
            raise TimeoutError(f"Could not find workflow run after {self.find_run_timeout_seconds}s")

        # 3. Wait for workflow to finish
        started_running = time.time()
        while run.status != "completed":
            if time.time() - started_running > self.run_timeout_seconds:
                raise TimeoutError(f"Workflow run timed out after {self.run_timeout_seconds}s")
            time.sleep(15)
            run = context.github_client.rest.actions.get_workflow_run(
                owner=self.owner, repo=self.repo, run_id=run.id
            ).parsed_data

        if run.conclusion != "success":
            raise Exception(f"Workflow failed with conclusion: {run.conclusion}")

        # 4. Find the latest release (which is likely a draft created by the action)
        releases_response = context.github_client.rest.repos.list_releases(
            owner=self.owner, repo=self.repo, per_page=1
        )
        releases = releases_response.parsed_data
        if not releases:
            raise ValueError("No releases found after workflow completed")

        latest_release = releases[0]

        asset_to_download = next(
            (a for a in latest_release.assets if a.name.endswith(".ipa")), None
        )
        if not asset_to_download:
            raise FileNotFoundError("No IPA asset found in the latest release")

        # 5. Download the IPA
        download_asset = context.github_client.rest.repos.get_release_asset(
            owner=self.owner,
            repo=self.repo,
            asset_id=asset_to_download.id,
            headers={"Accept": "application/octet-stream"},
        )

        file_path = context.work_dir / asset_to_download.name
        sha256 = hashlib.sha256()
        with open(file_path, "wb") as f:
            for chunk in download_asset.iter_bytes():
                f.write(chunk)
                sha256.update(chunk)

        context.current_ipa_path = file_path

        file_info = FileInfo(
            path=file_path,
            url=asset_to_download.browser_download_url,
            sha256=sha256.hexdigest(),
        )

        context.step_results.append(StepResult(name="githubaction", data=[file_info]))
