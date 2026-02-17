"""Test publishing to TestPyPI."""
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


@pytest.mark.skipif(
    not os.environ.get("TEST_PYPI_TOKEN"),
    reason="TEST_PYPI_TOKEN not set",
)
class TestPyPIPublishing:
    """Test package building and TestPyPI publishing."""

    def test_build_package(self):
        """Package must build successfully."""
        result = subprocess.run(
            ["uv", "build"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Build failed: {result.stderr}"

        dist_path = ROOT / "dist"
        assert dist_path.exists(), "dist/ directory not created"

        wheels = list(dist_path.glob("*.whl"))
        tarballs = list(dist_path.glob("*.tar.gz"))

        assert len(wheels) > 0, "No wheel file created"
        assert len(tarballs) > 0, "No source distribution created"

    def test_publish_to_testpypi(self):
        """Package must publish to TestPyPI successfully."""
        token = os.environ.get("TEST_PYPI_TOKEN")

        # Build first
        subprocess.run(["uv", "build"], cwd=ROOT, capture_output=True)

        # Publish to TestPyPI
        result = subprocess.run(
            [
                "uv",
                "publish",
                "--publish-url",
                "https://test.pypi.org/legacy/",
                "--token",
                token,
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

        # Allow "already exists" as success (idempotent)
        success = result.returncode == 0 or "already exists" in result.stderr
        assert success, f"Publish failed: {result.stderr}"
