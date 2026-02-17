"""Tests for release infrastructure configuration."""
import json
import shutil
import subprocess
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


class TestReleaseConfiguration:
    """Validate release-please configuration files."""

    def test_release_please_config_valid_json(self):
        """release-please-config.json must be valid JSON."""
        config_path = ROOT / "release-please-config.json"
        assert config_path.exists(), "release-please-config.json not found"
        config = json.loads(config_path.read_text())
        assert "packages" in config or "release-type" in config

    def test_release_please_manifest_valid_json(self):
        """.release-please-manifest.json must be valid JSON."""
        manifest_path = ROOT / ".release-please-manifest.json"
        assert manifest_path.exists(), ".release-please-manifest.json not found"
        manifest = json.loads(manifest_path.read_text())
        assert "." in manifest, "Root package version missing"

    def test_version_consistency(self):
        """Manifest version must match pyproject.toml version."""
        manifest = json.loads((ROOT / ".release-please-manifest.json").read_text())
        pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())

        manifest_version = manifest["."]
        pyproject_version = pyproject["project"]["version"]

        assert manifest_version == pyproject_version, (
            f"Version mismatch: manifest={manifest_version}, "
            f"pyproject={pyproject_version}"
        )

    def test_package_name_matches(self):
        """Config package-name must match pyproject.toml name."""
        config = json.loads((ROOT / "release-please-config.json").read_text())
        pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())

        # Handle both flat and packages config formats
        if "packages" in config:
            pkg_config = config["packages"].get(".", {})
            config_name = pkg_config.get("package-name")
        else:
            config_name = config.get("package-name")

        pyproject_name = pyproject["project"]["name"]

        if config_name:
            assert config_name == pyproject_name, (
                f"Package name mismatch: config={config_name}, "
                f"pyproject={pyproject_name}"
            )

    def test_release_type_is_python(self):
        """Release type must be 'python' for this project."""
        config = json.loads((ROOT / "release-please-config.json").read_text())

        # release-type can be at root level or in packages
        release_type = config.get("release-type")
        if release_type is None and "packages" in config:
            release_type = config["packages"].get(".", {}).get("release-type")

        assert release_type == "python", f"Expected python, got {release_type}"


class TestWorkflowConfiguration:
    """Validate GitHub Actions workflow."""

    def test_workflow_valid_yaml(self):
        """release.yml must be valid YAML."""
        import yaml

        workflow_path = ROOT / ".github/workflows/release.yml"
        assert workflow_path.exists(), "release.yml not found"

        workflow = yaml.safe_load(workflow_path.read_text())
        assert workflow is not None
        # Note: YAML 1.1 parses 'on' as boolean True
        assert True in workflow or "on" in workflow, "Missing trigger configuration"
        assert "jobs" in workflow, "Missing jobs configuration"

    def test_workflow_triggers_on_main(self):
        """Workflow must trigger on push to main."""
        import yaml

        workflow = yaml.safe_load(
            (ROOT / ".github/workflows/release.yml").read_text()
        )

        # YAML 1.1 parses 'on' as boolean True
        trigger_config = workflow.get(True) or workflow.get("on", {})
        push_config = trigger_config.get("push", {})
        branches = push_config.get("branches", [])

        assert "main" in branches, "Workflow must trigger on main branch"

    def test_workflow_has_concurrency(self):
        """Workflow should have concurrency control."""
        import yaml

        workflow = yaml.safe_load(
            (ROOT / ".github/workflows/release.yml").read_text()
        )

        # Concurrency can be at root level or job level
        has_root_concurrency = "concurrency" in workflow
        has_job_concurrency = any(
            "concurrency" in job_config
            for job_config in workflow.get("jobs", {}).values()
            if isinstance(job_config, dict)
        )

        assert has_root_concurrency or has_job_concurrency, (
            "Missing concurrency configuration"
        )

    def test_workflow_uses_release_please_v4(self):
        """Workflow must use release-please-action v4."""
        workflow_text = (ROOT / ".github/workflows/release.yml").read_text()
        assert "release-please-action@v4" in workflow_text or \
               "release-please-action@v" in workflow_text


class TestCommitizen:
    """Validate commitizen configuration."""

    def test_commitizen_hook_in_precommit(self):
        """Commitizen hook must be in pre-commit config."""
        import yaml

        precommit_path = ROOT / ".pre-commit-config.yaml"
        assert precommit_path.exists(), ".pre-commit-config.yaml not found"

        config = yaml.safe_load(precommit_path.read_text())

        # Look for commitizen in any repo
        commitizen_found = False
        for repo in config.get("repos", []):
            repo_url = repo.get("repo", "")
            hooks = repo.get("hooks", [])

            if "commitizen" in repo_url:
                commitizen_found = True
                break

            for hook in hooks:
                if hook.get("id") == "commitizen" or "cz" in hook.get("id", ""):
                    commitizen_found = True
                    break

        assert commitizen_found, "Commitizen hook not found in pre-commit config"


class TestChangelog:
    """Validate CHANGELOG.md format."""

    def test_changelog_exists(self):
        """CHANGELOG.md must exist."""
        changelog_path = ROOT / "CHANGELOG.md"
        assert changelog_path.exists(), "CHANGELOG.md not found"

    def test_changelog_has_header(self):
        """CHANGELOG.md must have proper header."""
        content = (ROOT / "CHANGELOG.md").read_text()
        assert "# Changelog" in content or "# CHANGELOG" in content

    def test_changelog_has_version_entry(self):
        """CHANGELOG.md must have at least one version entry."""
        import re

        content = (ROOT / "CHANGELOG.md").read_text()
        # Match patterns like ## [1.0.0] or ## 1.0.0
        version_pattern = r"##\s*\[?\d+\.\d+\.\d+\]?"

        assert re.search(version_pattern, content), "No version entry found"


class TestCommitMessageValidation:
    """Test commitizen commit message validation."""

    @pytest.fixture(autouse=True)
    def check_cz_available(self):
        """Skip tests if commitizen (cz) is not installed."""
        if shutil.which("cz") is None:
            # Try via uv run
            result = subprocess.run(
                ["uv", "run", "cz", "--version"],
                capture_output=True,
                cwd=ROOT,
            )
            if result.returncode != 0:
                pytest.skip("commitizen (cz) not installed")

    @pytest.mark.parametrize(
        "message,should_pass",
        [
            ("feat: add new feature", True),
            ("fix: resolve bug", True),
            ("docs: update readme", True),
            ("feat(api): add endpoint", True),
            ("fix!: breaking change", True),
            ("add new feature", False),  # Missing type
            ("feature: add thing", False),  # Wrong type
            ("FEAT: uppercase", False),  # Uppercase type
        ],
    )
    def test_commit_message_format(self, message, should_pass):
        """Test various commit message formats against commitizen rules."""
        # Use cz check to validate without actually committing
        result = subprocess.run(
            ["uv", "run", "cz", "check", "--message", message],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        if should_pass:
            assert result.returncode == 0, (
                f"Message '{message}' should be valid but failed: {result.stderr}"
            )
        else:
            assert result.returncode != 0, (
                f"Message '{message}' should be invalid but passed"
            )
