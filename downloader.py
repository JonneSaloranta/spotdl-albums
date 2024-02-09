import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from decouple import config
import requests
from spotdl import Spotdl

# Your Spotify API credentials
client_id = config('SPOTIFY_CLIENT_ID')
client_secret = config('SPOTIFY_CLIENT_SECRET')

# Download path from .env file
download_path = config('DOWNLOAD_PATH')

class Downloader():
    def __init__(self):
        downloader_settings = {
            "output": download_path,
        }

        client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        self.spotdl = Spotdl(client_id=client_id, client_secret=client_secret, downloader_settings=downloader_settings)

    def get_playlist_tracks(self, playlist_url):
        playlist_id = playlist_url.split('/')[-1].split('?')[0]
        results = self.sp.playlist_tracks(playlist_id)
        tracks = results['items']
        while results['next']:
            results = self.sp.next(results)
            tracks.extend(results['items'])
        return tracks

    def get_playlist_albums_urls(self, playlist_url):
        album_urls = []
        playlist_id = playlist_url.split('/')[-1].split('?')[0]
        tracks = self.get_playlist_tracks(playlist_id)
        for track in tracks:
            album_info = track['track']['album']
            album_url = album_info['external_urls']['spotify']
            if album_url not in album_urls:
                album_urls.append(album_url)
        return album_urls

    def download_album(self, album_url):
        songs = self.spotdl.search([album_url])
        self.spotdl.download_songs(songs)

    def fetch_playlist_urls(self, gist_url):
        response = requests.get(gist_url)
        if response.status_code == 200:
            return response.text.strip().split('\n')
        else:
            print(f"Failed to fetch playlist URLs. Status Code: {response.status_code}")
            return []

    def download_all(self):
        gist_url = config('PLAYLISTS_URL')
        playlist_urls = self.fetch_playlist_urls(gist_url)
        for playlist_url in playlist_urls:
            album_urls = self.get_playlist_albums_urls(playlist_url)
            for album_url in album_urls:
                print(f'Downloading album: {album_url}')
                self.download_album(album_url)

if __name__ == '__main__':
    downloader = Downloader()
    print('Downloader initialized')
    downloader.download_all()
