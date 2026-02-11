#!/usr/bin/env python3
import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request

BASE_COMMIT = "f9c855f7cf04d603c9546bc01776c74806a879c1"


def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, check=True, text=True, capture_output=True)


def get_git_head(repo):
    return run(["git", "rev-parse", "HEAD"], cwd=repo).stdout.strip()


def is_clean(repo):
    status = run(["git", "status", "--porcelain"], cwd=repo).stdout.strip()
    return status == ""


def apply_patch(repo, patch_path):
    run(["git", "apply", "--whitespace=nowarn", patch_path], cwd=repo)


def download_patch(url, dst_path):
    with urllib.request.urlopen(url) as resp, open(dst_path, "wb") as f:
        shutil.copyfileobj(resp, f)

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_sha256_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip().split()[0]


def is_url(path_or_url: str) -> bool:
    return path_or_url.startswith("http://") or path_or_url.startswith("https://")


def parse_args():
    parser = argparse.ArgumentParser(description="Apply GradLoc patch to verl.")
    parser.add_argument("--repo", required=True, help="Path to verl git repo")
    parser.add_argument("--patch-url", default="", help="HTTP(S) URL for the patch file")
    parser.add_argument("--patch-file", default="", help="Local patch file path")
    parser.add_argument("--patch-sha256", default="", help="Expected patch sha256 hex string")
    parser.add_argument("--sha256-file", default="", help="Path/URL to sha256 file")
    parser.add_argument("--force", action="store_true", help="Skip base commit and clean checks")
    return parser.parse_args()


def main():
    args = parse_args()
    repo = os.path.abspath(args.repo)

    if not os.path.isdir(repo):
        print(f"Repo not found: {repo}", file=sys.stderr)
        return 1

    if not args.force:
        head = get_git_head(repo)
        if head != BASE_COMMIT:
            print(f"Repo HEAD is {head}, expected {BASE_COMMIT}", file=sys.stderr)
            print("Use --force to bypass this check.", file=sys.stderr)
            return 2
        if not is_clean(repo):
            print("Repo has uncommitted changes. Please clean or use --force.", file=sys.stderr)
            return 3

    patch_file = args.patch_file
    sha256_expected = args.patch_sha256
    sha256_file_path = args.sha256_file
    temp_dir = None
    try:
        if args.patch_url:
            temp_dir = tempfile.mkdtemp(prefix="gradloc_patch_")
            patch_file = os.path.join(temp_dir, "gradloc.patch")
            print(f"Downloading patch: {args.patch_url}")
            download_patch(args.patch_url, patch_file)
            if sha256_file_path and is_url(sha256_file_path):
                sha_path = os.path.join(temp_dir, "gradloc.patch.sha256")
                download_patch(sha256_file_path, sha_path)
                sha256_expected = read_sha256_file(sha_path)
        else:
            if not patch_file:
                patch_file = os.path.join(os.path.dirname(__file__), "patches", "gradloc.patch")
            if not sha256_file_path:
                local_sha = patch_file + ".sha256"
                if os.path.isfile(local_sha):
                    sha256_file_path = local_sha

        if not os.path.isfile(patch_file):
            print(f"Patch file not found: {patch_file}", file=sys.stderr)
            return 4
        if sha256_file_path and not sha256_expected:
            if is_url(sha256_file_path):
                temp_dir = temp_dir or tempfile.mkdtemp(prefix="gradloc_sha256_")
                sha_path = os.path.join(temp_dir, "gradloc.patch.sha256")
                download_patch(sha256_file_path, sha_path)
                sha256_expected = read_sha256_file(sha_path)
            else:
                if not os.path.isfile(sha256_file_path):
                    print(f"SHA256 file not found: {sha256_file_path}", file=sys.stderr)
                    return 5
                sha256_expected = read_sha256_file(sha256_file_path)

        if sha256_expected:
            actual = sha256_file(patch_file)
            if actual != sha256_expected:
                print("SHA256 mismatch for patch file.", file=sys.stderr)
                print(f"Expected: {sha256_expected}", file=sys.stderr)
                print(f"Actual:   {actual}", file=sys.stderr)
                return 6

        print(f"Applying patch: {patch_file}")
        apply_patch(repo, patch_file)
        print("Patch applied successfully.")
        return 0
    finally:
        if temp_dir and os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    raise SystemExit(main())
