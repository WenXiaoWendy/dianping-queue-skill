#!/usr/bin/env python3
"""Thin public wrapper for the closed-source dianping-queue helper."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
STATE_DIR = Path(os.environ.get("DIANPING_QUEUE_HOME", Path.home() / ".dianping-queue"))
HELPER_PATH = STATE_DIR / "helper" / "dianping-queue-helper"
VERSION_PATH = STATE_DIR / "helper" / "VERSION"
MANIFEST_PATH = SKILL_DIR / "helper-manifest.json"
SETUP_SCRIPT = SKILL_DIR / "scripts" / "setup_runtime.py"


def manifest_version() -> str:
    try:
        return str(json.loads(MANIFEST_PATH.read_text(encoding="utf-8")).get("version") or "").strip()
    except Exception:
        return ""


def installed_version() -> str:
    try:
        return VERSION_PATH.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return ""


def ensure_helper() -> None:
    expected = manifest_version()
    current = installed_version()
    if HELPER_PATH.exists() and os.access(HELPER_PATH, os.X_OK) and (not expected or current == expected):
        return
    result = subprocess.run([sys.executable, str(SETUP_SCRIPT)], text=True)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main(argv: list[str]) -> int:
    ensure_helper()
    env = os.environ.copy()
    env["DIANPING_QUEUE_SKILL_DIR"] = str(SKILL_DIR)
    completed = subprocess.run([str(HELPER_PATH), *argv], env=env, text=True)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
