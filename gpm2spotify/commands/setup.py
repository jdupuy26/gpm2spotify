import os

import click
import spotipy
from dynaconf import settings
from getmac import get_mac_address
from gmusicapi import Mobileclient
from spotipy.util import prompt_for_user_token

CWD = os.getcwd()
GPM_TOKEN = f"{CWD}/{settings.TOKEN_PATH}/gpm.cred"
SPOTIFY_TOKEN = f"{CWD}/{settings.TOKEN_PATH}/spotify.cred"


@click.command(help="Setup command for initializing credentials")
@click.option(
    "-n",
    "--no-oauth",
    help="Do not setup oauth, if token files already exist.",
    is_flag=True,
    default=False,
    show_default=True,
)
@click.option(
    "-s",
    "--spotify-only",
    help="Only setup for Spotify, as it expires more quickly.",
    is_flag=True,
    default=False,
    show_default=True,
)
def main(no_oauth, spotify_only):
    if settings.SPOTIPY_CLIENT_ID == "<your-spotify-client-id>":
        click.echo(
            click.style(
                "To use this CLI utility, you must have a client account setup with Spotify.\n"
                "Setup a developer client account at: "
                "https://developer.spotify.com/my-applications\n"
                "Then, specify the client_id and client_secret in 'settings.local.yaml'",
                bold=True,
            )
        )
        return
    # setup for Google Play Music
    if not spotify_only:
        mobile_client = Mobileclient()
        if not no_oauth:
            if not os.path.exists(f"{CWD}/{settings.TOKEN_PATH}"):
                os.makedirs(f"{CWD}/{settings.TOKEN_PATH}")
            mobile_client.perform_oauth(storage_filepath=f"{GPM_TOKEN}")

        # Make sure that login works
        device_id = get_mac_address().replace(":", "").upper()

        try:
            assert mobile_client.oauth_login(device_id, oauth_credentials=GPM_TOKEN)
        except Exception:
            click.echo(
                click.style(
                    "ERROR: login for Google Play Music hit an exception.", fg="red", bold=True
                )
            )
            raise

        click.echo(click.style("Success logging into Google Play Music!", fg="green", bold=True))
        click.echo(f"Oauth file for GPM stored in: '{GPM_TOKEN}'")

    # setup for Spotify
    try:
        if not no_oauth:
            token = prompt_for_user_token(
                settings.SPOTIPY_CLIENT_USERNAME,
                client_id=settings.SPOTIPY_CLIENT_ID,
                client_secret=settings.SPOTIPY_CLIENT_SECRET,
                redirect_uri=settings.SPOTIPY_REDIRECT_URI,
                cache_path=f"{SPOTIFY_TOKEN}",
                scope=settings.SPOTIPY_SCOPE,
            )
        else:
            token = spotipy.oauth2.SpotifyOAuth(
                username=settings.SPOTIPY_CLIENT_USERNAME,
                client_id=settings.SPOTIPY_CLIENT_ID,
                client_secret=settings.SPOTIPY_CLIENT_SECRET,
                redirect_uri=settings.SPOTIPY_REDIRECT_URI,
                cache_path=f"{SPOTIFY_TOKEN}",
            ).get_access_token()["access_token"]
        # verify that login works
        spotify = spotipy.Spotify(auth=token)
        assert bool(spotify.current_user())
    except Exception:
        click.echo(click.style("ERROR: login for Spotify hit an exception.", fg="red", bold=True))
        raise

    click.echo(click.style(f"Success logging into Spotify!", fg="green", bold=True))
    click.echo(f"Oauth file for Spotify stored in: '{SPOTIFY_TOKEN}'")
