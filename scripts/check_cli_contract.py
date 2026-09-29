#!/usr/bin/env python3
"""Check documented CLI spellings offline via help, without running actions."""

from pathlib import Path
import os
import shlex
import socket
import subprocess
import tempfile
from unittest.mock import patch

from click.testing import CliRunner
from notebooklm.notebooklm_cli import cli


def main():
    root = Path(__file__).resolve().parents[1]
    reference = root / "skills/notebooklm-learning/references/cli.md"
    commands = list(dict.fromkeys(
        line.strip() for line in reference.read_text(encoding="utf-8").splitlines()
        if line.startswith("notebooklm ")
    ))
    if not commands:
        raise SystemExit("No documented commands found")
    failures = []
    with tempfile.TemporaryDirectory(prefix="nlm-contract-") as tmp:
        state = str(Path(tmp) / "unused-storage.json")
        env = {"NOTEBOOKLM_HOME": tmp, "NOTEBOOKLM_PROFILE": "contract-test"}
        with patch.dict(os.environ, env), \
             patch.object(socket.socket, "connect", side_effect=AssertionError("Network disabled")), \
             patch.object(socket.socket, "connect_ex", side_effect=AssertionError("Network disabled")), \
             patch.object(subprocess, "Popen", side_effect=AssertionError("Subprocess disabled")):
            for command in commands:
                args = ["--storage", state, *shlex.split(command)[1:], "--help"]
                result = CliRunner().invoke(cli, args)
                if result.exit_code:
                    failures.append((command, result.output, repr(result.exception)))
            # Guard the version-specific pitfall the recipe deliberately avoids.
            invalid = CliRunner().invoke(cli, [
                "--storage", state, "generate", "quiz", "--language", "zh_Hans", "--help"
            ])
            if invalid.exit_code == 0 or not (
                "No such option" in invalid.output and "--language" in invalid.output
            ):
                failures.append(("quiz --language contract changed", invalid.output, ""))
    for command, output, error in failures:
        print(f"FAIL: {command}\n{output}\n{error}")
    if failures:
        raise SystemExit(1)
    print(f"PASS: {len(commands)} documented commands + quiz language regression check")
    print("Offline option/help checks only; authentication, server behavior and learning quality not tested.")


if __name__ == "__main__":
    main()
