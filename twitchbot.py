import spotipy
from spotipy.oauth2 import SpotifyOAuth
from twitchio.ext import commands
import os

# Spotify authentication
scope = "user-modify-playback-state,user-read-currently-playing"
spotify = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(scope=scope, redirect_uri = 'http://localhost'))

def skip_song():
    print(" o Skip to next")
    spotify.next_track()
    
def restart_song():
    print(" o Song restart")
    spotify.previous_track()

def what_song():
    print(" - Song query")
    return "Aktuálně hraje " + spotify.current_user_playing_track()['item']['name'] + " od " +  spotify.current_user_playing_track()['item']['artists'][0]['name']

def try_add_song_to_queue(search):
    track_id = spotify.search(q=search, type='track')

    if ( len(track_id['tracks']['items']) < 1 ):
        print(" x " + search + " not found")
        return "Na " + search + " jsem nic nenašel"

    spotify.add_to_queue('spotify:track:' + track_id['tracks']['items'][0]['id'],device_id=None)
    print(" o " + track_id['tracks']['items'][0]['artists'][0]['name'] + " - " + track_id['tracks']['items'][0]['name'] + " queued")
    
    return track_id['tracks']['items'][0]['name'] + " od " + track_id['tracks']['items'][0]['artists'][0]['name'] + " přidán do fronty!"


class Bot(commands.Bot):

    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        super().__init__(token=os.environ['TWITCHIO_TOKEN'], prefix='!', initial_channels=['vahisht'])

    async def event_ready(self):
        # We are logged in and ready to chat and use commands.
        print(f'Logged in as {self.nick}')

    # Handles the Spotify functionality.
    @commands.command(name='spotify')
    async def handle_spotify_command(self, ctx: commands.Context):

        # Get the asking user.
        asker = await self.fetch_users(names=[ctx.author.name])
        print(" - User " + ctx.author.name.upper() + " trying to use " + ctx.message.content)

        data = ctx.message.content.split(' ')

        # Not enough arguments supplied. Show help.
        if (len(data) <= 1) and not ctx.author.is_subscriber and not ctx.author.is_mod:
            return   

        if (len(data) > 1) and data[1].lower() == "song":
            await ctx.send("@" + ctx.author.name + " " + what_song() )
            return

        # Only SUBSCRIBER and MODERATOR allowed from this point on.
        if not ctx.author.is_subscriber and not ctx.author.is_mod:
            await ctx.send('Sorry @' + ctx.author.name + ', tahle funkce je jenom pro suby a mody.')
            return

        # Not enough arguments supplied. Show help.
        if (len(data) <= 1):
            await ctx.send('@' + ctx.author.name + ' spotify příkaz se používá jako !spotify add <jméno písničky>')
            print(" x Not enough arguments in call " + ctx.message.content)
            return   

        # Adds song to the queue.
        if data[1].lower() == "add":
            if (len(data) <= 2):
                return
            await ctx.send("@" + ctx.author.name + " " + try_add_song_to_queue(" ".join(data[2:])))
            return

        # Only MODERATOR functions from this point on.
        if not ctx.author.is_mod:
            await ctx.send('Sorry @' + ctx.author.name + ', tahle funkce je jenom pro mody.')
            return

        # Skips song.
        if data[1].lower() == "skip":
            skip_song()
            await ctx.send("@" + ctx.author.name + " Skipuju na další")
            return

        # Repeats current song.
        if data[1].lower() == "again":
            await ctx.send("@" + ctx.author.name + " Pouštím aktuální song znovu od začátku")
            return

        print(" x No match for command " + data[1].lower())
        await ctx.send('@' + ctx.author.name + ' hm?')


# Twitch Chat bot init and run
bot = Bot()
bot.run()
