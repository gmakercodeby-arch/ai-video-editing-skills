---
name: youtube-auto-uploader
description: >-
  Automated YouTube video & Shorts uploader using the official YouTube Data API v3 (OAuth2).
  Generates High-CTR Hinglish titles, SEO descriptions, hashtags (#Shorts / #MovieExplained),
  optional Creative Commons attribution, and uploads custom 1280x720 thumbnails for long-form
  videos. Defaults to private/unlisted for safety before publishing. Activate when preparing,
  scheduling, or uploading finished Shorts or Movie Explained videos to YouTube.
---

# YouTube Auto-Uploader Skill (YouTube Data API v3)

Use this skill after a video passes `qa_inspect_video.py` (`status == "PASS"`) to upload it directly to YouTube with optimized Hinglish metadata and optional custom thumbnail.

## Prerequisites
1. Install dependencies in `.venv`:
   `pip install google-api-python-client google-auth-oauthlib google-auth-httplib2`
2. Create an OAuth 2.0 Desktop App credential in Google Cloud Console (YouTube Data API v3 enabled) and save it as `client_secrets.json` in your working directory (never commit `client_secrets.json` or `yt_token.json` to Git).

## Usage
```powershell
python pipeline/youtube_upload.py "<video.mp4>" --title "<Hinglish Title>" --desc "<Description>" --tags "movie explained,hindi recap,shorts" --privacy private --thumbnail "<optional_thumb.jpg>"
```

## Safety & SEO Rules
- **Default Privacy:** Always default to `--privacy private` (or `unlisted`) unless the user explicitly asks for `public`.
- **Shorts Detection:** Include `#Shorts` in the title or description for vertical (`<= 3 min`) videos.
- **Copyright Attribution:** For Creative Commons (`CC BY`) sources, include the mandatory attribution line in the description automatically.
- **Long-Form Thumbnails:** Attach a `1280×720` high-CTR thumbnail (`--thumbnail`) for 16:9 Movie Explained videos.
