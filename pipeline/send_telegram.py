# -*- coding: utf-8 -*-
"""send_telegram.py - deliver a finished Short via Telegram Bot API.
Reads TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID from environment variables or .env / config.json.
"""
import json
import os
import sys
import requests


def load_creds():
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not (token and chat_id) and os.path.exists(".env"):
        for line in open(".env", encoding="utf-8"):
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1)
                if k.strip() == "TELEGRAM_BOT_TOKEN":
                    token = v.strip().strip('"').strip("'")
                elif k.strip() == "TELEGRAM_CHAT_ID":
                    chat_id = v.strip().strip('"').strip("'")
    if not (token and chat_id) and os.path.exists("telegram_config.json"):
        cfg = json.load(open("telegram_config.json", encoding="utf-8"))
        token = token or cfg.get("bot_token", "")
        chat_id = chat_id or str(cfg.get("chat_id", ""))
    if not token or not chat_id:
        raise RuntimeError("Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env or environment!")
    return token, chat_id


if __name__ == "__main__":
    token, chat_id = load_creds()
    video_path = sys.argv[1]
    caption = sys.argv[2] if len(sys.argv) > 2 else "Rendered Video"
    with open(video_path, "rb") as f:
        r = requests.post(
            f"https://api.telegram.org/bot{token}/sendVideo",
            data={"chat_id": chat_id, "supports_streaming": True, "caption": caption},
            files={"video": (os.path.basename(video_path), f, "video/mp4")},
            timeout=180,
        )
    print("TELEGRAM_STATUS:", r.status_code, r.json().get("ok"), "message_id:", r.json().get("result", {}).get("message_id"))
