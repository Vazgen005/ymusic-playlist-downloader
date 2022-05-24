import yandex_music
import logging
import json
import sys
import os
import re

logging.getLogger().setLevel(logging.DEBUG)

symbols = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
url = ''

if os.path.exists('config.json'):
    with open('config.json', 'r') as f:
        try:
            token = json.load(f)['token']
        except json.decoder.JSONDecodeError:
            token = input('Enter token: ')
        except KeyError:
            token = input('Enter token: ')
else:
    token = input('Enter token: ')


try:
    client = yandex_music.Client(token).init()
except yandex_music.exceptions.UnauthorizedError:
    print('Invalid token')
    sys.exit(1)

with open('config.json', 'w') as f:
    f.write(json.dumps({'token': token}))

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

def download_music():
    def fix_string(string):
        for symbol in symbols:
            string = string.replace(symbol, '')
        return string

    def fix_track_info(track_info: dict):
        if track_info['playlist_title'] == '' or track_info['playlist_title'] == None:
            track_info['playlist_title'] = 'unnamed'

        for key in track_info:
            if isinstance(track_info[key], str):
                track_info[key] = fix_string(track_info[key])
        
        return track_info

    def get_music_directory():
        return f'{os.getcwd()}\\music\\'

    def join_artists(artists: list):
        return ', '.join(list(map(lambda x: fix_string(x['name']), artists)))

    def get_path_for_playlist(track_info: dict):
        path: str = f'{get_music_directory()}{track_info["playlist_title"]}'
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def get_path_for_tack(track_info: dict):
        return f"{get_path_for_playlist(track_info)}\\{join_artists(track_info['track_artists'])} - {track_info['track_title']}.mp3"

    for track in playlist.tracks:
        track_info = {
            'track_artists': track['track']['artists'],
            'track_title': track['track']['title'],
            'playlist_title': playlist['title'],
        }

        track_info = fix_track_info(track_info)

        if not os.path.exists(get_path_for_tack(track_info)):
            try:
                track['track'].download(get_path_for_tack(track_info))
            except yandex_music.exceptions.TimedOutError:
                print('Timed out. Retrying...')
                download_music()
            except yandex_music.exceptions.NetworkError:
                print('Network error. Retrying...')
                download_music()
            print(f"Downloaded: {os.path.basename(get_path_for_tack(track_info)).replace('.mp3', '')}")
        else:
            print(f"Already downloaded: {os.path.basename(get_path_for_tack(track_info)).replace('.mp3', '')}")


if __name__ == '__main__':
    download_music()

print('Done!')
