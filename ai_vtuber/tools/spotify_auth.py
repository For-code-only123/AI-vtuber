import spotipy
from spotipy.oauth2 import SpotifyOAuth

# 填入你的信息
CLIENT_ID = "4eb22388535748e69c9ba43576b6a254"
CLIENT_SECRET = "71849a46fae14a42bbb4c6078dbbdde9"
REDIRECT_URI = "http://127.0.0.1:8888/callback"

SCOPE = "user-modify-playback-state user-read-playback-state user-read-currently-playing"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE
))

# 测试连接
devices = sp.devices()
print("可用设备：")
for device in devices["devices"]:
    print(f"  - {device['name']} ({device['type']}) ID: {device['id']}")