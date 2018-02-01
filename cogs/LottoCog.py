import discord
from discord.ext import commands
from random import randint
from numpy.random import choice
import numpy as np
import sqlite3


class LottoCog:
    min_buy_in = 0.1
    max_buy_in = 10

    fee = 0.1  # 1% fee

    def __init__(self, bot):
        self.bot = bot
        self.grlc = bot.grlc
        self.conn = bot.conn
        self.dbname = bot.dbname
        c = self.conn.cursor()
        c.exucute("CREATE TABLE IF NOT EXISTS main.lotto_games (current INT, winnerUserId INT)")
        c.execute("CREATE TABLE IF NOT EXISTS main.lotto_entries (userId INT , amount REAL, gameId INT)")
        self.conn.commit()

    def lotto_restart(self, conn):
        """
        Create a game of lotto if none exists,

        """
        c = conn.cursor()
        c.execute("UPDATE lotto_games SET current = 0 WHERE current = 1")
        c.execute("INSERT INTO lotto_games VALUES (1, ?, ?)", (None, datetime.now() + timedelta(hours=1)))
        conn.commit()
        c.execute("SELECT rowid, * FROM lotto_games WHERE current = 1")
        return c.fetchone()

    async def lotto_winner(self):
        c = self.conn.cursor()
        entrants = []
        amounts = []
        game = self.get_current_game()
        for row in c.execute("SELECT * FROM lotto_entries WHERE gameId = ?", (game['rowid'],)):
            entrants.append(row['userId'])
            amounts.append(row['amount'])
        if len(amounts) > 0:

            amounts = np.array(amounts)
            value = amounts.sum()
            winnerId = choice(entrants, p=value / amounts)
            c.execute("UPDATE lotto_games SET winnerId = ?", (winnerId,))
            self.conn.commit()
            # move the coins from the losers to the winnerId
            for idx, playerId in enumerate(entrants):
                if playerId != winnerId:
                    self.grlc.move_between_accounts(playerId, winnerId, amounts[idx])
            bot_fee = value * self.fee
            value -= bot_fee
            self.grlc.move_between_accounts(winnerId, self.bot.accountID, bot_fee)
            return winnerId, value
        else:
            return None, 0

    @commands.command()
    async def enterlotto(self, ctx, *, amount: float):
        """
        Start a dicegame, another player must accept it
        :param message:
        :return:
        """
        # check if the user already has a game in progress
        current_game = self.get_current_game(self.conn)
        if current_game is None:
            await ctx.send(f'{ctx.author.mention}: There\'s no lottery running at the moment')
            return
        if amount <= self.min_buy_in and amount > self.max_buy_in:
            await ctx.send(
                f"{ctx.author.mention}: Entries must be between {self.min_buy_in} and {self.max_buy_in} GRLC")
            return
        balance = self.grlc.get_balance(ctx.author.id)
        fee = amount * self.bot.bot_fee
        if balance < amount + fee:
            await ctx.send("{}: You have insufficient GRLC ({} + {} fee)".format(ctx.author.mention, balance, fee))
        else:
            c.execute("INSERT INTO lotto_entries VALUES (?, ?, ?)",
                      (ctx.author.id,
                       amount,
                       current_game.rowid)
                      )
            self.conn.commit()
            msg = "{} your entry {} GRLC has been received!".format(ctx.author.mention, amount)
            await ctx.send(msg)

    @commands.command()
    async def lottopot(self, ctx):
        """
        Show the pot and end time for the current lottery
        """
        game = self.get_current_game()
        total = 0
        c = self.conn.cursor()
        for row in c.execute("SELECT * FROM main.lotto_entries WHERE game = ?", (game['rowid'],)):
            total += row['amount']
        msg = "Current lottery has a pot of {} and will be draw in {}".format(total, datetime.now() - game.drawtime)
        await ctx.send(msg)

    def get_current_game(self):
        c = self.conn.cursor()
        c.execute("SELECT rowid, * FROM main.lotto_games WHERE current = 1")
        game = c.fetchone()
        if game is None:
            game = self.lotto_restart()
        return game


def setup(ctx):
    ctx.add_cog(LottoCog(ctx))
