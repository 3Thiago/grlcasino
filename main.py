import traceback
import discord
import sys
from discord.ext import commands
import asyncio
import yaml
import sqlite3

with open('keys.yaml', 'r') as config_file:
    conf = yaml.load(config_file)

db_name = 'grlcasino.db'


def init_db():
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    for i in """CREATE TABLE main.users (username TEXT not null, address TEXT not null, CONSTRAINT name_uq UNIQUE (username))
CREATE TABLE main.history (username TEXT not null, action TEXT not null)
CREATE TABLE main.games (usernameA TEXT, usernameB TEXT, value REAL, winner TEXT, created DATETIME not null)""".splitlines():
        c.execute(i)
    conn.commit()




bot = commands.Bot(command_prefix='c!', description='Play Dice with GRLC')


@bot.event
async def on_ready():
    """http://discordpy.readthedocs.io/en/rewrite/api.html#discord.on_ready"""

    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')


extensions = ['cogs.dice']
if __name__ == "__main__":
    import os

    if not os.path.exists(db_name):
        init_db()
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            traceback.print_exc()

    bot.run(conf['token'], bot=True, reconnect=True)
