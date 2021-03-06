#!/usr/bin/env python
import traceback
import discord
import sys
from discord.ext import commands
import asyncio
import os
import yaml
import sqlite3
from utils import GarlicoinWrapper

with open('keys.yaml', 'r') as config_file:
    conf = yaml.load(config_file)

db_name = conf['dbname']


def init_db():
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    for i in ["CREATE TABLE main.history (userId INT not null, action TEXT not null)",
              "CREATE TABLE main.dice (userIdA INT, userIdB INT, value REAL, winnerUserId INT, created TIMESTAMP not null, rollA TEXT, rollB TEXT)",
              ""]:
        print(i)
        c.execute(i)
    conn.commit()
    conn.close()


if not os.path.exists(db_name):
    print("Building DB")
    init_db()

bot = commands.Bot(command_prefix='$',
                   description='Play Casino Games with GRLC. Put $ before commands\n'
                               'This bot will manage your coins for you and cost no network fees \n'
                               'until you withdraw your GRLC. You can think of it as an online wallet\n'
                               'Use $address to get an address and start playing!', )
conn = sqlite3.connect(db_name, detect_types=sqlite3.PARSE_DECLTYPES)
conn.row_factory = sqlite3.Row
grlc = GarlicoinWrapper(conf['rpcUrl'], conf['rpcUser'], conf['rpcPass'])

bot.conn = conn
bot.grlc = grlc
bot.dbname = db_name
bot.bot_id = conf['botId']
bot.bot_fee = float(conf['botFee'])


@bot.event
async def on_ready():
    """http://discordpy.readthedocs.io/en/rewrite/api.html#discord.on_ready"""

    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')


extensions = [
    'cogs.DiceCog',
    'cogs.CasinoCog',
    'cogs.LottoCog',
    'cogs.TwoUpCog',
    'cogs.CoinTossCog'
]
if __name__ == "__main__":

    for extension in extensions:
        try:
            bot.load_extension(extension)
            print(f"Loaded extension: {extension}")
        except Exception as e:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            traceback.print_exc()

    bot.run(conf['token'], bot=True, reconnect=True)
