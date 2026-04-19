"""Validator compatibility test: fixture must pass scripts/validate_splits.py exactly."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# Paths relative to this test file's location.
_TESTS_DIR = Path(__file__).parent
_FIXTURES_DIR = _TESTS_DIR / "fixtures"
_REPO_ROOT = _TESTS_DIR.parents[2]  # smig/datasets/validation -> smig/datasets -> smig -> repo root
_FIXTURE = _FIXTURES_DIR / "synthetic_manifest.json"
_SCRIPT = _REPO_ROOT / "scripts" / "validate_splits.py"


class TestFixturePassesValidator:
    def test_fixture_file_exists(self):
        assert _FIXTURE.exists(), f"Fixture not found: {_FIXTURE}"

    def test_script_exists(self):
        assert _SCRIPT.exists(), f"Validator script not found: {_SCRIPT}"

    def test_validate_splits_exits_zero(self):
        result = subprocess.run(
            [sys.executable, str(_SCRIPT), str(_FIXTURE)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"validate_splits.py exited {result.returncode}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    def test_no_leakage_in_stderr(self):
        result = subprocess.run(
            [sys.executable, str(_SCRIPT), str(_FIXTURE)],
            capture_output=True,
            text=True,
        )
        assert "leakage" not in result.stderr.lower(), (
            f"'leakage' found in stderr:\n{result.stderr}"
        )

    def test_no_warning_in_stderr(self):
        result = subprocess.run(
            [sys.executable, str(_SCRIPT), str(_FIXTURE)],
            capture_output=True,
            text=True,
        )
        assert "warning" not in result.stderr.lower(), (
            f"'warning' found in stderr:\n{result.stderr}"
        )

    def test_ok_message_in_stdout(self):
        result = subprocess.run(
            [sys.executable, str(_SCRIPT), str(_FIXTURE)],
            capture_output=True,
            text=True,
        )
        assert "OK" in result.stdout, (
            f"Expected 'OK' in stdout, got: {result.stdout!r}"
        )
