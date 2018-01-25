import traceback
import discord
import sys
from discord.ext import commands
import asyncio
import yaml
import sqlite3
from utils import GarlicoinWrapper, UserManager

with open('keys.yaml', 'r') as config_file:
    conf = yaml.load(config_file)

db_name = 'grlcasino.db'


def init_db():
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    for i in """CREATE TABLE main.users (userId INT not null, address TEXT not null, CONSTRAINT name_uq UNIQUE (userId))
CREATE TABLE main.history (userId INT not null, action TEXT not null)
CREATE TABLE main.dice (userIdA INT, userIdB INT, value REAL, winnerUserId INT, created DATETIME not null, rollA TEXT, rollB TEXT)""".splitlines():
        print(i)
        c.execute(i)
    conn.commit()
    conn.close()


import os

if not os.path.exists(db_name):
    print("Building DB")
    init_db()

bot = commands.Bot(command_prefix='$', description='Play Casino Games with GRLC')
conn = sqlite3.connect(db_name)
grlc = GarlicoinWrapper('/scratch/garlicoin/bin/garlicoin-cli')
user_manager = UserManager(conn, grlc)

bot.conn = conn
bot.grlc = grlc
bot.user_manager = user_manager


@bot.event
async def on_ready():
    """http://discordpy.readthedocs.io/en/rewrite/api.html#discord.on_ready"""

    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')


extensions = ['cogs.DiceCog', 'cogs.CasinoCog']
if __name__ == "__main__":

    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            traceback.print_exc()

    bot.run(conf['token'], bot=True, reconnect=True)
