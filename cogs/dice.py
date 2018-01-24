import discord
from discord.ext import commands
import sqlite3
import subprocess


class DiceCog:
    def __init__(self, ctx):
        self.ctx = ctx
        self.conn = sqlite3.connect('grlcasino.db')

    def generate_wallet(self):
        return 'GWdkRUwDMdZWKRZmks2pX8iWawaSUQDkHt'
        return subprocess.check_output(['garlium', 'createnewaddress'])

    def get_user(self, user):
        c = self.conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (user.name,))
        user_row = c.fetchone()
        if user_row is None:
            return self.create_user(user)
        return user_row

    def get_balance(user):
        return 4.20

    def create_user(self, user):
        c = self.conn.cursor()
        wallet_addr = self.generate_wallet()
        c.execute("INSERT INTO users VALUES (?, ?)", (user.name, wallet_addr))
        self.conn.commit()
        return self.get_user(user)

    @commands.command(description='Withdraw all your coins to the specified address')
    async def withdraw(self, ctx, str):
        pass

    @commands.command()
    async def stats(self, ctx):
        await ctx.send(f"Stats for {ctx.author.mention}")

    @commands.command(description="Show your sending address", pass_context=True)
    async def address(self, ctx):
        user = ctx.message.author
        await ctx.send('{} Send Coins to: `{}`'.format(user.mention, self.get_user(user)[1]))

    @commands.command()
    async def addbalance(self, ctx):
        try:
            amount = float(ctx.message.content.split(' ')[1])
            if amount <= 0:
                raise ValueError
            c = self.conn.cursor()
            c.execute("SELECT * FROM users WHERE username = ?", (ctx.message.author.name,))
            row = c.fetchone()
            if row is None:
                self.create_user(ctx.message.author)
                newbal = amount
            else:
                newbal = + amount

            await ctx.send(f"{ctx.author.mention} added {amount} GRLC. Now at {newbal}")
        except ValueError:
            await ctx.send(f"{ctx.author.mention}: Please add a valid amount of GRLC")
        except IndexError:
            await ctx.send(f"{ctx.author.mention}: Usage is `c!addbalance <amount>`")

    @commands.command()
    async def balance(self, message):
        c = self.conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (message.author,))
        row = c.fetchone()
        if row is None:
            row = self.create_user(message.author)
        await ctx.send(message.author + "{}'s balance is: {} GRLC".format(message.author, row[1]))

    @commands.command()
    async def start(self, ctx):
        """
        Check if the user has enough coins to start
        :param message:
        :return:
        """

        try:
            pieces = ctx.message.content.split(' ')
            amount = float(pieces[1])
            balance = self.get_user(ctx.message.author)[1]
            if balance < amount:
                await ctx.send("You have insufficient GRLC ({})".format(balance))
            else:
                c = self.conn.cursor()
                c.execute("INSERT INTO games VALUES (?, ?, ?, ?)", (ctx.message.author, None, amount,))
                self.conn.commit()
        except ValueError:
            await ctx.send.send("Please specify a valid amount of GRLC")
        except IndexError:
            await ctx.send("Usage is c!start <balance>")

    @commands.command()
    async def accept(self, ctx):
        # if the user is not signed up, they can't play
        pieces = ctx.message.content.split(' ')
        if len(pieces) != 2:
            await ctx.send("Usage is `c!accept @username#1234`. You must have enough coins ")

    # @commands.command()
    # async def on_message(self, message):
    #     if message.content.startswith('c!help'):
    #         await ctx.send('Functions are: ' + (', '.join(ctx.command_prefix + c for c in ctx.commands)))


def setup(ctx):
    ctx.add_cog(DiceCog(ctx))
