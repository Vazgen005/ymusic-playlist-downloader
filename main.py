import yandex_music
import logging
import json
import sys
import os
import re

logging.getLogger().setLevel(logging.DEBUG)

symbols = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
url = ''


def config():
    if os.path.exists('config.json'):
        with open('config.json', 'r') as f:
            return json.load(f)['token']
    with open('config.json', 'w') as f:
        token = json.dumps({'token': input('Enter token: ')})
        f.write(token)
        return token


client = yandex_music.Client(config()).init()

if not url or url == '':
    url = input('Please, enter a url to a playlist: ')

regex = re.search('(https://)?(www\.)?music\.yandex\.ru/users/([A-Za-z0-9-_]+)/playlists/([0-9]+)?', url, re.IGNORECASE)

if regex:
    id_ = regex.group(4)
    owner = regex.group(3)
else:
    print('invalid url')
    sys.exit(1)

playlist = client.users_playlists(id_, owner)


def dw_music():
    for track in playlist.tracks:

        track_title = track['track']['title']
        track_artists = track['track']['artists']

        for symbol in symbols:
            if symbol in track_title:
                track_title = track_title.replace(symbol, '')
            if symbol in track_artists:
                track_artists = track_artists.replace(symbol, '')

        if not os.path.exists(
                f"{os.getcwd()}\\music\\{f'{playlist.title}' if not playlist.title == '' or None else f'unnamed'}\\{', '.join(list(map(lambda x: x['name'], track_artists)))} - {track_title}.mp3"):

            if not os.path.exists(
                    f"{os.getcwd()}\\music\\{f'{playlist.title}' if not playlist.title == '' or None else f'unnamed'}\\"):
                os.mkdir(
                    f"{os.getcwd()}\\music\\{f'{playlist.title}' if not playlist.title == '' or None else f'unnamed'}\\")

            try:
                track['track'].download(
                    f"{os.getcwd()}\\music\\{f'{playlist.title}' if not playlist.title == '' or None else f'unnamed'}\\{', '.join(list(map(lambda x: x['name'], track_artists)))} - {track_title}.mp3")
            except yandex_music.exceptions.TimedOutError:
                print('Timed out. Retrying...')
                dw_music()
            except yandex_music.exceptions.NetworkError:
                print('Network error. Retrying...')
                dw_music()
            print(f"Downloaded: {', '.join(list(map(lambda x: x['name'], track_artists)))} - {track_title}")
        else:
            print(f"Already downloaded: {', '.join(list(map(lambda x: x['name'], track_artists)))} - {track_title}")


if __name__ == '__main__':
    dw_music()

print('Done!')
