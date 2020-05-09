import click

from gpm2spotify.commands.playlist import main as playlist_main
from gpm2spotify.commands.setup import main as setup_main


@click.group()
def gpm2spotify():
    pass


gpm2spotify.add_command(setup_main, name="setup")
gpm2spotify.add_command(playlist_main, name="playlist")


if __name__ == "__main__":
    gpm2spotify()
