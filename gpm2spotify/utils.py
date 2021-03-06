""" After setup has been run, you can access the clients from here."""
import os

import spotipy
from dynaconf import settings
from getmac import get_mac_address
from gmusicapi import Mobileclient

CWD = os.getcwd()
GPM_TOKEN = f"{CWD}/{settings.TOKEN_PATH}/gpm.cred"
SPOTIFY_TOKEN = f"{CWD}/{settings.TOKEN_PATH}/spotify.cred"


def get_gpm_client():
    """ Fetch the Google Play Music Client"""
    gpm_client = Mobileclient()
    # Make sure that login works
    device_id = settings.GOOGLE_DEVICE_ID or get_mac_address().replace(":", "").upper()
    assert gpm_client.oauth_login(device_id, oauth_credentials=GPM_TOKEN)
    return gpm_client


def get_spotify_client():
    token = spotipy.oauth2.SpotifyOAuth(
        username=settings.SPOTIPY_CLIENT_USERNAME,
        client_id=settings.SPOTIPY_CLIENT_ID,
        client_secret=settings.SPOTIPY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIPY_REDIRECT_URI,
        cache_path=f"{SPOTIFY_TOKEN}",
    ).get_access_token()["access_token"]
    return spotipy.Spotify(auth=token)
