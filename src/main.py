from rich.progress import Progress
from rich.console import Console
import yandex_music
import asyncio
import json
import sys
import os
import re

console = Console()

class Client(yandex_music.Client):
    def __init__(self, token:str = "") -> None:
        yandex_music.Client.notice_displayed = True
        super().__init__(token)
        if self.isValidToken():
            Token.writeTokenToConfig(token)
            return
        console.log("Token is invalid\nExiting...")
        sys.exit(1)
             
    def isValidToken(self) -> bool:
        try:
            self._request.get(f"{self.base_url}/account/status")
        except yandex_music.exceptions.UnauthorizedError or yandex_music.exceptions.TimedOutError:
            return False
        return True

class Token:
    @staticmethod
    def getToken() -> str:
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                try:
                    token = json.load(f)['token']
                except json.decoder.JSONDecodeError or KeyError:
                    token = input('Enter token: ')
        else:
            token = input('Enter token: ')
        return token
        
    @staticmethod
    def writeTokenToConfig(token:str = "") -> None:
        with open('config.json', 'w') as f:
            f.write(json.dumps({'token': token}))

class StringOperations:
    @staticmethod
    def fixString(string):
        for symbol in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
            string = string.replace(symbol, '')
        return string

    @staticmethod
    def fixTrackInfo(track_info: dict):
        if track_info['playlist_title'] == '' or track_info['playlist_title'] == None:
            track_info['playlist_title'] = 'unnamed'
        for key in track_info:
            if isinstance(track_info[key], str):
                track_info[key] = StringOperations.fixString(track_info[key])
        return track_info
    
    @staticmethod
    def joinArtists(artists: list):
        return ', '.join(list(map(lambda x: StringOperations.fixString(x['name']), artists)))

    @staticmethod
    def getMusicDirectory():
        return f'{os.getcwd()}\\music\\'

class Downloads:
    def parsePlaylist(self, url):
        regex = re.search('(https://)?(www\.)?music\.yandex\.ru/users/([A-Za-z0-9-_]+)/playlists/([0-9]+)?', url, re.IGNORECASE)
        if regex:
            return client.users_playlists(regex.group(4), regex.group(3))
        else:
            console.log('Invalid url was given')
            sys.exit(1)

    def getPathForPlaylist(self, track_info: dict):
        path: str = f'{StringOperations.getMusicDirectory()}{track_info["playlist_title"]}'
        if not os.path.exists(path):
            os.makedirs(path)
        return path
        
    def getPathForTrack(self, track_info: dict):
        return f"{self.getPathForPlaylist(track_info)}\\{StringOperations.joinArtists(track_info['track_artists'])} - {track_info['track_title']}.mp3"

    async def downloadTracks(self, playlist):
        self.progressBar = Progress(console=console)
        self.progressBar.start()
        self.taskId = self.progressBar.add_task("[green]Downloading music...", total=len(playlist.tracks)) 
        await asyncio.gather(*[self.task(track, playlist) for track in playlist.tracks]) 
        self.progressBar.stop()
        
    async def task(self, track, playlist):
        track_info = {
        'track_artists': track['track']['artists'],
        'track_title': track['track']['title'],
        'playlist_title': playlist['title'],
        }
        exceptions = {
            yandex_music.exceptions.TimedOutError : "Timed out. Retrying...",
            yandex_music.exceptions.NetworkError: "Network error. Retrying...",
        }

        track_info = StringOperations.fixTrackInfo(track_info=track_info)

        if not os.path.exists(self.getPathForTrack(track_info)):
            try:
                track['track'].download(self.getPathForTrack(track_info))
                console.log(f"{os.path.basename(self.getPathForTrack(track_info)).replace('.mp3', '')}")
            except Exception as exception:
                console.log("\n", exceptions[exception] if exception in exceptions.keys() else f"Unknow error:\n{exception}")
                await asyncio.sleep(1)
                await self.task(track, playlist)
        else:        
            console.log(f"Already downloaded: {os.path.basename(self.getPathForTrack(track_info)).replace('.mp3', '')}")
        self.progressBar.update(self.taskId, advance = 1)

if __name__ == "__main__":
    client = Client(Token.getToken()).init()
    Downloads_ = Downloads()
    asyncio.run(Downloads_.downloadTracks(Downloads_.parsePlaylist(url=console.input("Please, enter a url to a playlist: "))))
    console.log('Done!')