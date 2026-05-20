# utils/youtube_helper.py
import re
import requests

def extract_video_id(url):
    pattern = r"(?:v=|youtu\.be\/)([0-9A-Za-z_-]{11})"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

def get_video_info(url):
    """Fetch video title, thumbnail, author using YouTube oEmbed API (free, no key needed)"""
    try:
        video_id = extract_video_id(url)
        if not video_id:
            return None
        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        r = requests.get(oembed_url, timeout=10)
        data = r.json()
        return {
            "title": data.get("title", ""),
            "author": data.get("author_name", ""),
            "thumbnail": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
        }
    except:
        return None

def get_transcript(url):
    """Returns video URL + title for AI to generate content."""
    video_id = extract_video_id(url)
    if not video_id:
        return None
    info = get_video_info(url)
    title = info["title"] if info else ""
    print(f"Video title: {title}")
    if title:
        return f"YOUTUBE_URL::{url}::TITLE::{title}"
    return f"YOUTUBE_URL::{url}"
