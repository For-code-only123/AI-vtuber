import spotipy
from spotipy.oauth2 import SpotifyOAuth
import yaml

def _load_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

config = _load_config()
CLIENT_ID = config["spotify"]["client_id"]
CLIENT_SECRET = config["spotify"]["client_secret"]
REDIRECT_URI = config["spotify"]["redirect_uri"]

SCOPE = "user-modify-playback-state user-read-playback-state user-read-currently-playing"
_sp = None

def get_spotify():
    global _sp
    if _sp is None:
        _sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope=SCOPE
        ))
    return _sp

def search_song(song_name: str) -> tuple[bool, dict | str]:
    sp = get_spotify()

    # 清理书名号
    clean_name = song_name.replace("《", "").replace("》", "").strip()

    # 精确搜索，加track:限定
    results = sp.search(q=f"track:{clean_name}", type="track", limit=5)
    tracks = results["tracks"]["items"]

    # 从结果里找名字最接近的
    if tracks:
        for track in tracks:
            if track["name"] == clean_name or clean_name in track["name"]:
                return True, {
                    "song_name": track["name"],
                    "artist": track["artists"][0]["name"],
                    "uri": track["uri"]
                }
        # 没有完全匹配的，用第一条
        track = tracks[0]
        return True, {
            "song_name": track["name"],
            "artist": track["artists"][0]["name"],
            "uri": track["uri"]
        }

    # 没找到
    return False, f"《{song_name}》没有搜索到"

def get_device_id() -> str | None:
    """动态获取当前活跃的Spotify设备ID"""
    sp = get_spotify()
    devices = sp.devices()
    for device in devices["devices"]:
        if device["is_active"]:
            return device["id"]
    # 没有活跃设备，取第一个
    if devices["devices"]:
        return devices["devices"][0]["id"]
    return None

def play_song(uri: str):
    device_id = get_device_id()
    if not device_id:
        print("[Spotify] 没有找到可用设备，请打开Spotify客户端")
        return
    sp = get_spotify()
    sp.start_playback(device_id=device_id, uris=[uri])

def set_volume(volume: int):
    device_id = get_device_id()
    if not device_id:
        return
    sp = get_spotify()
    sp.volume(volume, device_id=device_id)

def get_current_volume() -> int:
    sp = get_spotify()
    playback = sp.current_playback()
    if playback and playback.get("device"):
        return playback["device"]["volume_percent"]
    return 50

def is_playing() -> bool:
    sp = get_spotify()
    playback = sp.current_playback()
    return playback is not None and playback.get("is_playing", False)

def pause():
    sp = get_spotify()
    sp.pause_playback(device_id=DEVICE_ID)

def resume():
    sp = get_spotify()
    sp.start_playback(device_id=DEVICE_ID)