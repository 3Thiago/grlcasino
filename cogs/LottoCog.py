import discord
from discord.ext import commands
from random import randint
from datetime import datetime, timedelta
from numpy.random import choice
import numpy as np
import humanize
import asyncio
from .BaseCog import BaseCog


class LottoCog(BaseCog):
    min_buy_in = 0.1
    max_buy_in = 10

    fee = 0.1  # 1% fee

    def __init__(self, bot):
        self.bot = bot
        self.grlc = bot.grlc
        self.conn = bot.conn
        self.dbname = bot.dbname
        c = self.conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS main.lotto_games (current INT, winnerUserId INT, drawTime TIMESTAMP)")
        c.execute("CREATE TABLE IF NOT EXISTS main.lotto_entries (userId INT , amount REAL, gameId INT)")
        self.conn.commit()

    async def lotto_winner(self, ctx, gameId):
        c = self.conn.cursor()
        entrants = []
        amounts = []
        for row in c.execute("SELECT * FROM lotto_entries WHERE gameId = ?", (gameId,)):
            entrants.append(row['userId'])
            amounts.append(row['amount'])
        if len(amounts) > 0:

            amounts = np.array(amounts)
            value = amounts.sum()
            winnerId = choice(entrants, p=amounts / value)
            c.execute('UPDATE lotto_games SET current = 0, winnerUserId = ? WHERE rowid = ?', (winnerId, gameId,))
            msg = "Odds are: {}".format(','.join(self.bot.get_user(x).mention + f": {round(y*100,2)}%" for x,y in zip(entrants, amounts/value)))
            self.grlc.move_between_accounts(self.bot.bot_id, winnerId, value)
            winner = self.bot.get_user(winnerId)
            msg += f"{winner.mention} wins {round(value, 3)} GRLC, congratulations! {self.grlc_emoji}"
            await ctx.send(msg)
        else:
            await ctx.send("No entries received for lotto!")
            c.execute('UPDATE lotto_games SET current = 0, winnerUserId = ? WHERE rowid = ?', (None, gameId))
        self.conn.commit()

    @commands.command()
    async def lotto(self, ctx):
        """
        Start a lottery if non exists
        :param ctx:
        :return:
        """
        game = self.get_current_game()
        if game is None:
            # start a new game
            c = self.conn.cursor()
            delta = timedelta(minutes=1)
            draw_time = datetime.now() + delta
            c.execute("INSERT INTO lotto_games VALUES (1, ?, ?)", (None, draw_time))
            gameId = c.lastrowid
            self.conn.commit()
            await ctx.send("A lottery has begun! Enter with `$enterlotto amount`, will be drawn {}".format(
                humanize.naturaltime(draw_time)))
            await asyncio.sleep(int(delta.total_seconds()))
            await self.lotto_winner(ctx, gameId)

        else:
            await self.lottopot(ctx, game)

    @commands.command()
    async def enterlotto(self, ctx, *, amount: float):
        """
        Enter the current lottery
        :param message:
        :return:
        """
        # check if the user already has a game in progress
        current_game = self.get_current_game()
        if current_game is None:
            await ctx.send(f'{ctx.author.mention}: There\'s no lottery running at the moment')
            return
        if amount <= self.min_buy_in or amount > self.max_buy_in:
            await ctx.send(
                f"{ctx.author.mention}: Entries must be between {self.min_buy_in} and {self.max_buy_in} GRLC")
            return
        balance = await self.grlc.get_balance(ctx.author.id)
        fee = amount * self.bot.bot_fee
        if balance < amount + fee:
            await ctx.send("{}: You have insufficient GRLC ({} + {} fee)".format(ctx.author.mention, balance, fee))
        else:
            c = self.conn.cursor()
            c.execute("INSERT INTO lotto_entries VALUES (?, ?, ?)",
                      (ctx.author.id,
                       amount,
                       current_game['rowid'])
                      )
            self.conn.commit()
            self.grlc.move_between_accounts(ctx.author.id, self.bot.bot_id, amount + fee)
            msg = "{} your entry {} GRLC has been received!".format(ctx.author.mention, amount)
            await ctx.send(msg)

    async def lottopot(self, ctx, game):
        """
        Show the pot and end time for the current lottery
        """
        total = 0
        c = self.conn.cursor()
        msg = "Current entries to the lottery are:\n"
        for row in c.execute("SELECT * FROM main.lotto_entries WHERE gameId = ?", (game['rowid'],)):
            user = self.bot.get_user(row['userId'])
            msg += f"{user.mention}: {row['amount']} GRLC\n"
            total += row['amount']
        msg += "Current lottery has a pot of {} GRLC and will be drawn {}".format(round(total, 8), humanize.naturaltime(
            datetime.now() - game['drawtime']))
        await ctx.send(msg)
        if datetime.now() > game['drawTime']:
            await self.lotto_winner(ctx, game['rowid'])

    def get_current_game(self):
        c = self.conn.cursor()
        c.execute("SELECT rowid, * FROM main.lotto_games WHERE current = 1")
        return c.fetchone()


def setup(ctx):
    ctx.add_cog(LottoCog(ctx))
