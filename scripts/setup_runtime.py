#!/usr/bin/env python3
"""Install or update the closed-source dianping-queue helper."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import stat
import sys
import tempfile
import urllib.request
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
MANIFEST_PATH = SKILL_DIR / "helper-manifest.json"
STATE_DIR = Path(os.environ.get("DIANPING_QUEUE_HOME", Path.home() / ".dianping-queue"))
HELPER_DIR = STATE_DIR / "helper"
HELPER_PATH = HELPER_DIR / "dianping-queue-helper"
VERSION_PATH = HELPER_DIR / "VERSION"


def current_platform() -> str:
    system = platform.system().lower()
    machine = platform.machine().lower()
    if system == "darwin":
        os_name = "darwin"
    elif system == "linux":
        os_name = "linux"
    else:
        raise SystemExit(f"暂不支持当前系统：{platform.system()}")

    if machine in {"arm64", "aarch64"}:
        arch = "arm64"
    elif machine in {"x86_64", "amd64"}:
        arch = "x64"
    else:
        raise SystemExit(f"暂不支持当前架构：{platform.machine()}")
    return f"{os_name}-{arch}"


def read_manifest() -> dict:
    try:
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"缺少 helper-manifest.json：{MANIFEST_PATH}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def installed_version() -> str:
    try:
        return VERSION_PATH.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return ""


def helper_is_current(version: str) -> bool:
    return HELPER_PATH.exists() and os.access(HELPER_PATH, os.X_OK) and installed_version() == version


def download(url: str, target: Path) -> None:
    with urllib.request.urlopen(url) as response, target.open("wb") as out:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)


def install(force: bool) -> int:
    manifest = read_manifest()
    version = str(manifest.get("version") or "").strip()
    if not version:
        raise SystemExit("helper-manifest.json 缺少 version")

    platform_key = current_platform()
    platform_info = (manifest.get("platforms") or {}).get(platform_key)
    if not platform_info:
        raise SystemExit(f"当前平台没有可用 helper：{platform_key}")

    if helper_is_current(version) and not force:
        print(json.dumps({"status": "ok", "helper": str(HELPER_PATH), "version": version}, ensure_ascii=False))
        return 0

    url = str(platform_info.get("url") or "").strip()
    expected_sha256 = str(platform_info.get("sha256") or "").strip().lower()
    if not url:
        raise SystemExit(f"当前平台 helper 下载地址为空：{platform_key}")
    if not expected_sha256:
        raise SystemExit("helper-manifest.json 缺少 sha256；请先发布 helper 并更新 manifest")

    HELPER_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix="dianping-queue-helper-", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        download(url, tmp_path)
        actual_sha256 = sha256_file(tmp_path)
        if expected_sha256 and actual_sha256 != expected_sha256:
            raise SystemExit(
                f"helper sha256 校验失败：expected={expected_sha256} actual={actual_sha256}"
            )
        tmp_path.replace(HELPER_PATH)
        mode = HELPER_PATH.stat().st_mode
        HELPER_PATH.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        VERSION_PATH.write_text(version + "\n", encoding="utf-8")
        print(json.dumps({"status": "installed", "helper": str(HELPER_PATH), "version": version}, ensure_ascii=False))
        return 0
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description="Install dianping-queue helper")
    parser.add_argument("--force", action="store_true", help="force reinstall")
    args = parser.parse_args()
    return install(args.force)


if __name__ == "__main__":
    raise SystemExit(main())
