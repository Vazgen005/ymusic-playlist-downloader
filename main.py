import yandex_music
import logging
import json
import os

logging.getLogger().setLevel(logging.DEBUG)


def config():
    if os.path.exists('config.json'):
        with open('config.json', 'r') as f:
            return json.load(f)['token']
    with open('config.json', 'w') as f:
        token = json.dumps({'token': input('Enter token: ')})
        f.write(token)
        return token


client = yandex_music.Client(config()).init()


playlist = client.users_playlists(1234, 'music-blog')

for track in playlist.tracks:
    if not os.path.exists(f"music/{', '.join(list(map(lambda x: x['name'], track['track']['artists'])))} - {track['track']['title']}.mp3"):
        track['track'].download(f"music/{', '.join(list(map(lambda x: x['name'], track['track']['artists'])))} - {track['track']['title']}.mp3")
        print(f"Downloaded: {', '.join(list(map(lambda x: x['name'], track['track']['artists'])))} - {track['track']['title']}")
    else:
        print(f"Already downloaded: {', '.join(list(map(lambda x: x['name'], track['track']['artists'])))} - {track['track']['title']}")

print('Done!')
