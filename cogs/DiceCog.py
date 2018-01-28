import discord
from discord.ext import commands
from random import randint
from datetime import datetime
import asyncio

class DiceCog:
    dice = {
        1: '⚀',
        2: '⚁',
        3: '⚂',
        4: '⚃',
        5: '⚄',
        6: '⚅',
    }
    min_buy_in = 0.05
    max_buy_in = 10

    def __init__(self, bot):
        self.bot = bot
        self.grlc = bot.grlc
        self.conn = bot.conn

    @staticmethod
    def _roll_string():
        return "{}{}".format(randint(1, 6), randint(1, 6))

    @commands.command()
    async def start(self, ctx, *, amount: float):
        """
        Start a dicegame, another player must accept it
        :param message:
        :return:
        """
        # check if the user already has a game in progress
        current_game = self.get_current_game(ctx.author.id)
        if current_game is not None:
            await ctx.send(f'{ctx.author.mention}: Someone must accept your previous game before you can start another')
            return
        if amount <= self.min_buy_in and amount > self.max_buy_in:
            await ctx.send(
                f"{ctx.author.mention}: Games are have a must be between {self.min_buy_in} and {self.max_buy_in} GRLC")
            return
        balance = self.grlc.get_balance(ctx.author.id)
        if False and balance < amount:
            await ctx.send("{}: You have insufficient GRLC ({})".format(ctx.author.mention, balance))
        else:
            c = self.conn.cursor()
            rollA = self._roll_string()
            rollB = self._roll_string()
            while rollA == rollB:
                rollB = self._roll_string()

            c.execute("INSERT INTO dice VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (ctx.author.id,
                       None,
                       amount,
                       None,
                       datetime.now(),
                       rollA, rollB)
                      )
            self.conn.commit()
            msg = f"{ctx.author.mention} has started a game worth {amount}. Someone else must accept with '$accept {ctx.author.mention}' to complete the game"
            print(msg)
            await ctx.send(msg)

    @commands.command()
    async def accept(self, ctx, *, user: discord.User):
        """
        Accept the current dice game of the specified player
        :param ctx:
        :param user:
        :return:
        """
        # get the game row for the other user where there is no winner
        if user.id == ctx.author.id:
            await ctx.send(f'{ctx.author.mention}: You can\'t accept your own game')
            return
        row = self.get_current_game(ctx.author.id)

        if row is None:
            await ctx.send(f'{ctx.author.mention}: {user.mention} has no games currently')
            return
        # if the user is not signed up, they can't play
        player_b_balance = self.grlc.get_balance(ctx.author.id)
        if player_b_balance < row.value:
            await ctx.send(f'{ctx.author.id} you have insufficient funds to play ({row.value} GRLC). You have {player_b_balance} GRLC')
        else:
            # Play the game!!!!
            def str2score(score):
                return sum([int(x) for x in score])
            def str2emoji(score):
                return "{}{}".format(self.dice[score[0]], self.dice[score[1]])
            a_score = str2score(row['rollA'])
            b_score = str2score(row['rollB'])
            a_user = ctx.bot.get_user(id)
            msg = "{} rolled: {}, {} rolled: {}, ".format(
                a_user.mention,
                str2emoji(row['rollA']),
                ctx.author.mention,
                str2emoji(row['rollB'])
            )
            if a_score > b_score:
                winner = a_user
            else:
                winner = ctx.author
            msg += "{} wins {} GRLC!".format(winner)
            await ctx.send(msg)

    def get_current_game(self, id):
        c = self.conn.cursor()
        c.execute("SELECT * FROM dice WHERE userIdA = ? AND winnerUserId IS NULL", (id,))
        return c.fetchone()


def setup(ctx):
    ctx.add_cog(DiceCog(ctx))
