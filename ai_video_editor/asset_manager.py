import os
import logging
import requests

logger = logging.getLogger(__name__)

ASSETS_DIR = "assets"
os.makedirs(ASSETS_DIR, exist_ok=True)


def download_file(url: str, dest_path: str) -> str:
    """Stream-download a file from url to dest_path."""
    with requests.get(url, stream=True, timeout=30) as r:
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return dest_path


def get_audio_asset(query: str, media_type: str) -> str | None:
    """Query Pixabay for audio and return the local path of the first result."""
    api_key = os.environ["PIXABAY_API_KEY"]
    params = {
        "key": api_key,
        "q": query,
        "media_type": media_type,
        "per_page": 3,
    }
    resp = requests.get("https://pixabay.com/api/videos/", params=params, timeout=10)
    resp.raise_for_status()
    hits = resp.json().get("hits", [])
    if not hits:
        logger.warning(f"No Pixabay results for query='{query}' type='{media_type}'")
        return None

    hit = hits[0]
    url = hit.get("videos", {}).get("medium", {}).get("url") or hit.get("pageURL")
    ext = url.split(".")[-1].split("?")[0]
    dest = os.path.join(ASSETS_DIR, f"{media_type}_{query}_{hit['id']}.{ext}")
    return download_file(url, dest)


def get_sfx(query: str) -> str | None:
    return get_audio_asset(f"{query} sound", "sound")


def get_music(mood: str) -> str | None:
    return get_audio_asset(mood, "music")


def get_b_roll(keyword: str, portrait: bool = False) -> str | None:
    """Query Pexels for B-roll video footage and return the local path."""
    api_key = os.environ["PEXELS_API_KEY"]
    headers = {"Authorization": api_key}
    params = {"query": keyword, "per_page": 5, "orientation": "portrait" if portrait else "landscape"}
    resp = requests.get("https://api.pexels.com/videos/search", headers=headers, params=params, timeout=10)
    resp.raise_for_status()
    videos = resp.json().get("videos", [])
    if not videos:
        logger.warning(f"No Pexels results for keyword='{keyword}'")
        return None

    # Prefer HD quality
    video = videos[0]
    files = sorted(video.get("video_files", []), key=lambda f: f.get("width", 0), reverse=True)
    hd = next((f for f in files if f.get("quality") == "hd"), files[0])
    url = hd["link"]
    ext = url.split(".")[-1].split("?")[0]
    dest = os.path.join(ASSETS_DIR, f"broll_{keyword}_{video['id']}.{ext}")
    return download_file(url, dest)
