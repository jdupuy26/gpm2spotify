import sys

import click

from gpm2spotify.utils import get_gpm_client
from gpm2spotify.utils import get_spotify_client


@click.group(help="Commands for manipulating playlists")
def main():
    pass


@main.command(help="Create a playlist in Spotify from one that exists in Google Play Music")
@click.argument("playlist_name")
@click.option(
    "-d",
    "--dryrun",
    is_flag=True,
    help="Just list the songs from GPM for which you want the playlist in Spotify to be created.",
    show_default=True,
    default=False,
)
@click.option(
    "-sp", "--spotify-playlist-name", help="The name for the new spotify playlist", default=None
)
def copy(playlist_name, dryrun, spotify_playlist_name):
    if not spotify_playlist_name:
        spotify_playlist_name = playlist_name
    # first make sure the playlist exists in GPM
    desired_playlist = None

    gpm_client, spotify_client = get_gpm_client(), get_spotify_client()

    gpm_playlists = gpm_client.get_all_user_playlist_contents()
    for playlist in gpm_playlists:
        if playlist.get("name") == playlist_name:
            desired_playlist = playlist
    if not desired_playlist:
        click.echo(
            click.style(
                f"ERROR: playlist '{playlist_name}' not found on your GPM account",
                fg="red",
                bold=True,
            )
        )
        sys.exit(1)

    # make sure the playlist actually has tracks in it!
    if not desired_playlist.get("tracks"):
        click.echo(
            click.style(
                f"ERROR: playlist '{playlist_name}' does not have any tracks to copy!",
                fg="red",
                bold=True,
            )
        )
        sys.exit(1)

    desired_track_ids = [track["trackId"] for track in desired_playlist["tracks"]]

    # gather the information for each track in the playlist
    tracks = [track for track in gpm_client.get_all_songs() if track.get("id") in desired_track_ids]
    for track_id in desired_track_ids:
        try:
            tracks.append(gpm_client.get_track_info(track_id))
        except Exception:
            pass

    if dryrun:
        click.echo(
            click.style(
                f"Success, {len(tracks)} tracks found!\nIf this wasn't a dryrun, "
                f"I would create a playlist in Spotify with the following tracks:",
                bold=True,
            )
        )
        for track in tracks:
            click.echo(
                f"-    title: {track.get('title')}, "
                f"artist: {track.get('artist')}, album: {track.get('album')}"
            )

    # get the spotify track ids
    spotify_track_ids = []
    for track in tracks:
        # TODO: improve searching
        search_result = spotify_client.search(
            q=f"{track['title']} artist:{track['artist']}", type="track", limit=1
        )
        if search_result["tracks"]["total"] == 0:
            click.echo(click.style(f"Track: '{track['title']}' not found on Spotify", fg="yellow"))
        else:
            click.echo(
                click.style(
                    f"Found track: '{search_result['tracks']['items'][0]['name']}' on Spotify",
                    fg="green",
                )
            )
            if search_result["tracks"]["items"][0]["id"] not in spotify_track_ids:
                spotify_track_ids.append(search_result["tracks"]["items"][0]["id"])

    if not spotify_track_ids:
        click.echo(
            click.style("ERROR: No tracks were found on Spotify, exiting...", fg="red", bold=True)
        )
        sys.exit(1)

    # now create the new playlist in spotify
    if not dryrun:
        user_id = spotify_client.current_user()["id"]
        spotify_playlist = spotify_client.user_playlist_create(user_id, spotify_playlist_name)
        try:
            spotify_client.user_playlist_add_tracks(
                user_id, spotify_playlist["id"], spotify_track_ids
            )
        except Exception:
            click.echo(
                click.style("ERROR: Adding tracks to Spotify playlist failed!", fg="red", bold=True)
            )
            raise
        click.echo(
            click.style(
                f"SUCCESS! View your playlist at: {spotify_playlist['external_urls']['spotify']}",
                fg="green",
                bold=True,
            )
        )
