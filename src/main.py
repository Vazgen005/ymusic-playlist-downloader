import yandex_music
import logging
import asyncio
import json
import sys
import os
import re


logging.getLogger().setLevel(logging.DEBUG)

class Client:
    def login(self):
        client = None
        token = ''
        
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
        return client

class StringOperations:
    def fix_string(self, string):
        for symbol in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
            string = string.replace(symbol, '')
        return string

    def fix_track_info(self, track_info: dict):
        if track_info['playlist_title'] == '' or track_info['playlist_title'] == None:
            track_info['playlist_title'] = 'unnamed'
        for key in track_info:
            if isinstance(track_info[key], str):
                track_info[key] = self.fix_string(track_info[key])
        return track_info

class Downloads:
    SO = StringOperations()
    def playlist_parser(self, url):
        id_ = 0
        owner = ''
        regex = re.search('(https://)?(www\.)?music\.yandex\.ru/users/([A-Za-z0-9-_]+)/playlists/([0-9]+)?', url, re.IGNORECASE)
        if regex:
            return client.users_playlists(regex.group(4), regex.group(3))
        else:
            print('invalid url')
            sys.exit(1)
        
    def get_music_directory(self):
        return f'{os.getcwd()}\\music\\'
    
    def join_artists(self, artists: list):
        return ', '.join(list(map(lambda x: self.SO.fix_string(x['name']), artists)))

    def get_path_for_playlist(self, track_info: dict):
        path: str = f'{self.get_music_directory()}{track_info["playlist_title"]}'
        if not os.path.exists(path):
            os.makedirs(path)
        return path
        
    def get_path_for_tack(self, track_info: dict):
        return f"{self.get_path_for_playlist(track_info)}\\{self.join_artists(track_info['track_artists'])} - {track_info['track_title']}.mp3"

    async def download_tracks(self, playlist):
        await asyncio.gather(*[self.task(track, playlist) for track in playlist.tracks]) 

    async def task(self, track, playlist):
        track_info = {
        'track_artists': track['track']['artists'],
        'track_title': track['track']['title'],
        'playlist_title': playlist['title'],
        }

        track_info = self.SO.fix_track_info(track_info=track_info)

        if not os.path.exists(self.get_path_for_tack(track_info)):
            try:
                track['track'].download(self.get_path_for_tack(track_info))
                print(f"Downloaded: {os.path.basename(self.get_path_for_tack(track_info)).replace('.mp3', '')}")
            except yandex_music.exceptions.TimedOutError:
                print('Timed out. Retrying...')
                await asyncio.sleep(1)
                await self.task(track, playlist)
            except yandex_music.exceptions.NetworkError:
                print('Network error. Retrying...')
                await asyncio.sleep(1)
                await self.task(track, playlist)
        else:
            print(f"Already downloaded: {os.path.basename(self.get_path_for_tack(track_info)).replace('.mp3', '')}")

if __name__ == "__main__":
    client = Client().login()
    Downloads_ = Downloads()
    asyncio.run(Downloads_.download_tracks(Downloads_.playlist_parser(url=input("Please, enter a url to a playlist: "))))
    print('Done!')