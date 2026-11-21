# -*- coding: utf-8 -*-
"""
youtube_upload.py - Official YouTube Data API v3 uploader with OAuth2 token caching,
resumable upload, custom thumbnail support, and safe default privacy='private'.
"""
import argparse
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def get_youtube_service(secrets_file="client_secrets.json", token_file="yt_token.json"):
    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(secrets_file):
                raise FileNotFoundError(
                    f"Missing {secrets_file}. Download OAuth Desktop credentials from Google Cloud Console."
                )
            flow = InstalledAppFlow.from_client_secrets_file(secrets_file, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_file, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
    return build("youtube", "v3", credentials=creds)


def upload_video(video_path, title, description, tags, category_id="24", privacy="private", thumbnail=None, secrets="client_secrets.json", token="yt_token.json"):
    youtube = get_youtube_service(secrets, token)
    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": [t.strip() for t in tags.split(",") if t.strip()],
            "categoryId": category_id,
            "defaultLanguage": "hi",
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        },
    }
    media = MediaFileUpload(video_path, chunksize=4 * 1024 * 1024, resumable=True)
    req = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            print(f"Upload progress: {int(status.progress() * 100)}%", flush=True)
    vid = resp["id"]
    print(f"UPLOAD_COMPLETE: https://youtu.be/{vid} (privacy={privacy})")
    if thumbnail and os.path.exists(thumbnail):
        youtube.thumbnails().set(videoId=vid, media_body=MediaFileUpload(thumbnail)).execute()
        print(f"THUMBNAIL_SET: {thumbnail}")
    return vid


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Upload video to YouTube via Data API v3")
    p.add_argument("video", help="Path to MP4 file")
    p.add_argument("--title", required=True)
    p.add_argument("--desc", default="")
    p.add_argument("--tags", default="movie explained in hindi,hindi movie recap,shorts")
    p.add_argument("--category", default="24")
    p.add_argument("--privacy", default="private", choices=["private", "unlisted", "public"])
    p.add_argument("--thumbnail", default=None)
    p.add_argument("--secrets", default="client_secrets.json")
    p.add_argument("--token", default="yt_token.json")
    args = p.parse_args()
    upload_video(args.video, args.title, args.desc, args.tags, args.category, args.privacy, args.thumbnail, args.secrets, args.token)
