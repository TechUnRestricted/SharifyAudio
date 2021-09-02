import random
import time
import requests
from configuration import Telegram, LastFM
from telethon import functions
from telethon.sync import TelegramClient

client = TelegramClient(Telegram.api_name, Telegram.api_id, Telegram.api_hash)
client.start()


def get_json(url):
    output = requests.get(url).json()
    return output


def char_trim(string, limit):
    # Trim string if it has more than N chars (and add '…' to the end)
    if len(string) > limit:
        return string[:limit] + "…"
    else:
        return string


def set_telegram(about, currentAction):
    client(functions.account.UpdateProfileRequest(
        last_name=f'[Now: {currentAction}]',
        about=about
    ))


def get_current_playing():
    limit = 23
    json = get_json(
        f"https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&api_key={LastFM.api_key}&user={LastFM.username}&limit=1&format=json")
    current_track = json["recenttracks"]["track"][0]

    artist = "Unknown Artist"
    track = "Unknown Track"

    common_name = None

    if ("@attr" in current_track) and ("nowplaying" in current_track["@attr"]) and (
            current_track["@attr"]["nowplaying"] == "true"):
        # Artist name
        if ("artist" in current_track) and ("#text" in current_track["artist"]) and (current_track["artist"]["#text"]):
            artist = char_trim(string=current_track["artist"]["#text"], limit=limit)

        # Track name
        if ("name" in current_track) and (current_track["name"]):
            # Checking if we can extend the limit (if Artist name string is less than {limit + 1})
            if ((limit + 1) - len(artist)) > 0:
                limit = limit + (limit - len(artist))
            track = char_trim(string=current_track["name"], limit=limit)

        common_name = "🎶 [" + track + "] — " + artist + " 🎶 on Spotify®"
    return common_name


last_track_name = None
audio_was_stopped = False
counter = 0

while True:
    counter += 1
    wait_time = random.randint(15, 60)

    currentTimeStamp = int(time.time())

    try:
        currentTrack = get_current_playing()
        if currentTrack:
            if (currentTrack != last_track_name) or audio_was_stopped:
                audio_was_stopped = False

                last_track_name = currentTrack
                print(f"[{counter}] <|Sleeping: {wait_time}|> {currentTrack}")
                set_telegram(about=currentTrack, currentAction="Spotify")

        else:
            audio_was_stopped = True
            set_telegram(about=Telegram.default_status, currentAction="Idle")

    except Exception as e:
        print(f"[ERROR]: {e}")
    time.sleep(wait_time)
