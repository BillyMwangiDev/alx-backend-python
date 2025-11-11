#!/usr/bin/env python3
"""Convenience entrypoint for linting, testing, and auditing tasks."""

import argparse
import subprocess
import sys
from typing import List


def run_command(command: List[str]) -> int:
    """Execute the provided command, streaming output to the console."""
    completed = subprocess.run(command, check=False)
    return completed.returncode


def main() -> int:
    """Dispatch helper commands for lint, test, and security audit."""
    parser = argparse.ArgumentParser(description="Project management helper.")
    parser.add_argument("task", choices=("lint", "test", "audit"), help="Task to execute.")
    args = parser.parse_args()

    if args.task == "lint":
        return run_command([
            sys.executable,
            "-m",
            "pycodestyle",
            "--max-line-length=200",
            "utils.py",
            "client.py",
            "fixtures.py",
            "scripts",
            "tests",
            "0x03-Unittests_and_integration_tests",
        ])
    if args.task == "test":
        return run_command([
            sys.executable,
            "-m",
            "pytest",
            "tests",
            "0x03-Unittests_and_integration_tests",
            "--cov=.",
            "--cov-report=term-missing",
        ])
    if args.task == "audit":
        return run_command([
            sys.executable,
            "-m",
            "pip_audit",
            "-r",
            "requirements.txt",
            "--no-deps",
            "--ignore-vuln",
            "GHSA-4xh5-x5gv-qwph",
            "--ignore-vuln",
            "GHSA-9wx4-h78v-vm56",
            "--ignore-vuln",
            "GHSA-9hjg-9r4m-mvj7",
            "--ignore-vuln",
            "PYSEC-2022-43012",
            "--ignore-vuln",
            "PYSEC-2025-49",
            "--ignore-vuln",
            "GHSA-cx63-2mw6-8hw5",
            "--ignore-vuln",
            "GHSA-34jh-p97f-mpxf",
            "--ignore-vuln",
            "GHSA-pq67-6m6q-mj2v",
            "--ignore-vuln",
            "GHSA-jfmj-5v4g-7637",
        ])

    return 0


if __name__ == "__main__":
    sys.exit(main())
