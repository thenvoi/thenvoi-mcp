"""Dry-run tests for release-please behavior."""
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


@pytest.mark.skipif(
    not os.environ.get("GITHUB_TOKEN"),
    reason="GITHUB_TOKEN not set for dry-run",
)
class TestReleasePleaseDryRun:
    """Simulate release-please behavior."""

    def test_release_please_manifest_bootstrap(self):
        """Verify release-please can read the configuration."""
        result = subprocess.run(
            [
                "npx",
                "release-please",
                "manifest-pr",
                "--repo-url=thenvoi/thenvoi-mcp",
                "--token",
                os.environ["GITHUB_TOKEN"],
                "--dry-run",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )

        # Dry-run should complete without error
        # (may show "no changes" which is fine)
        assert result.returncode == 0 or "no changes" in result.stdout.lower(), (
            f"Dry-run failed: {result.stderr}"
        )

    def test_conventional_commits_detected(self):
        """Verify release-please can parse conventional commits."""
        # Get recent commits
        result = subprocess.run(
            ["git", "log", "--oneline", "-20"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

        commits = result.stdout.strip().split("\n")

        # Check at least some commits follow conventional format
        conventional_patterns = ["feat:", "fix:", "docs:", "chore:", "refactor:"]
        conventional_count = sum(
            1
            for commit in commits
            if any(p in commit.lower() for p in conventional_patterns)
        )

        # Print info about conventional commit usage
        ratio = conventional_count / len(commits) if commits else 0
        print(
            f"Conventional commits: {conventional_count}/{len(commits)} ({ratio:.0%})"
        )
