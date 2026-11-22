#!/usr/bin/env python3
"""
Official Meta Instagram Graph API Reels Uploader (100% Safe, Zero Ban Risk)
Publishes vertical Instagram Reels automatically via Meta's Content Publishing API.

Prerequisites:
  1. An Instagram Professional/Creator/Business account linked to a Facebook Page.
  2. A Meta Long-Lived Access Token & Instagram Business Account ID.
  3. A publicly accessible HTTPS video URL (or use a public cloud storage/ngrok URL).

Credentials can be placed in .env:
  INSTAGRAM_ACCESS_TOKEN=your_token_here
  INSTAGRAM_ACCOUNT_ID=your_account_id_here
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

try:
    import requests
except ImportError:
    requests = None


API_VERSION = "v21.0"
BASE_URL = f"https://graph.facebook.com/{API_VERSION}"


def load_env_credentials() -> tuple[str, str]:
    token = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "").strip()
    account_id = os.environ.get("INSTAGRAM_ACCOUNT_ID", "").strip()
    env_file = Path(".env")
    if env_file.exists() and (not token or not account_id):
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("INSTAGRAM_ACCESS_TOKEN=") and not token:
                token = line.split("=", 1)[1].strip().strip('"').strip("'")
            elif line.startswith("INSTAGRAM_ACCOUNT_ID=") and not account_id:
                account_id = line.split("=", 1)[1].strip().strip('"').strip("'")
    return token, account_id


def create_reel_container(video_url: str, caption: str, token: str, account_id: str, share_to_feed: bool = True) -> str:
    url = f"{BASE_URL}/{account_id}/media"
    payload = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "share_to_feed": "true" if share_to_feed else "false",
        "access_token": token,
    }
    resp = requests.post(url, data=payload, timeout=30)
    data = resp.json()
    if "id" not in data:
        raise RuntimeError(f"Instagram container creation failed: {data}")
    return data["id"]


def wait_for_processing(container_id: str, token: str, max_wait_sec: int = 180) -> None:
    url = f"{BASE_URL}/{container_id}"
    params = {"fields": "status_code,status", "access_token": token}
    start = time.time()
    print(f"[INFO] Waiting for Instagram to process video container {container_id}...")
    while time.time() - start < max_wait_sec:
        resp = requests.get(url, params=params, timeout=15)
        data = resp.json()
        code = data.get("status_code", "")
        if code == "FINISHED":
            print("[OK] Video processing complete!")
            return
        if code in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Instagram media processing failed: {data}")
        print(f"       Status: {code or 'IN_PROGRESS'} (waiting 6s)...")
        time.sleep(6)
    raise TimeoutError(f"Video processing exceeded {max_wait_sec}s timeout.")


def publish_reel(container_id: str, token: str, account_id: str) -> str:
    url = f"{BASE_URL}/{account_id}/media_publish"
    payload = {"creation_id": container_id, "access_token": token}
    resp = requests.post(url, data=payload, timeout=30)
    data = resp.json()
    if "id" not in data:
        raise RuntimeError(f"Failed to publish reel: {data}")
    return data["id"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Upload Reel to Instagram via Official Meta Graph API")
    parser.add_argument("--url", required=True, help="Public HTTPS URL of the video (MP4/MOV)")
    parser.add_argument("--caption", required=True, help="Hinglish caption with hashtags")
    parser.add_argument("--token", help="Meta Access Token (or set in .env)")
    parser.add_argument("--account-id", help="Instagram Business Account ID (or set in .env)")
    parser.add_argument("--no-feed", action="store_true", help="Do not share to main profile grid")
    args = parser.parse_args()

    if requests is None:
        print("[ERROR] requests package not installed. Run: pip install requests", file=sys.stderr)
        return 1

    token = args.token
    acc_id = args.account_id
    if not token or not acc_id:
        env_token, env_acc = load_env_credentials()
        token = token or env_token
        acc_id = acc_id or env_acc

    if not token or not acc_id:
        print("[ERROR] Missing Instagram credentials!", file=sys.stderr)
        print("        Provide via --token and --account-id, or set in .env:", file=sys.stderr)
        print("        INSTAGRAM_ACCESS_TOKEN=...", file=sys.stderr)
        print("        INSTAGRAM_ACCOUNT_ID=...", file=sys.stderr)
        return 1

    try:
        print(f"[1/3] Creating Reels container for {args.url}...")
        cid = create_reel_container(args.url, args.caption, token, acc_id, share_to_feed=not args.no_feed)
        print(f"[2/3] Container ID: {cid}")
        wait_for_processing(cid, token)
        print("[3/3] Publishing Reel...")
        post_id = publish_reel(cid, token, acc_id)
        print(f"\n[SUCCESS] Instagram Reel published live! Post ID: {post_id}")
        return 0
    except Exception as exc:
        print(f"\n[ERROR] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
