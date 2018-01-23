import discord
import asyncio
import yaml
import sqlite3

with open('keys.yaml', 'r') as config_file:
    conf = yaml.load(config_file)
client = discord.Client()

db_name = 'grlcasino.db'
conn = sqlite3.connect(db_name)


def init_db():
    c = conn.cursor()
    for i in """CREATE TABLE users (username TEXT not null, balance REAL, address TEXT not null, CONSTRAINT name_uq UNIQUE username)
CREATE TABLE history (username TEXT not null, action TEXT not null)
CREATE TABLE games (usernameA TEXT, usernameB TEXT, value REAL, winner TEXT, created DATETIME not null)""".splitlines():
        c.execute(i)
    conn.commit()


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


def generate_wallet():
    return 'GWdkRUwDMdZWKRZmks2pX8iWawaSUQDkHt'


@client.event
async def on_message(message):
    def do_addr(message):
        client.send_message(message.channel, '{} Send Coins to: {}')

    def get_user(username):
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        if user is None:
            return create_user()
        return user


    def create_user(username):
        c = conn.cursor()
        wallet_addr = generate_wallet()
        c.execute("INSERT INTO users VALUES (?, ?, ?)", (message.author, 0, wallet_addr))
        conn.commit()
        
    def add_balance(message):
        try:
            amount = float(message.content.split(' ')[1])
            if amount <= 0:
                raise ValueError
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username = ?", (message.author,))
            row = c.fetchone()
            if row is None:
                create_user(message.author)
                newbal = amount
            else:
                newbal = row[1] + amount

            client.send_message(message.channel,
                                message.author + "{} added {} GRLC. Now at {}".format(message.author, message.content,
                                                                                      newbal))
        except ValueError:
            client.send_message(message.channel,
                                message.author + "{}: Please add a valid amount of GRLC".format(message.author))

    def do_balance(message):
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (message.author,))
        row = c.fetchone()
        if row is None:
            row = create_user(message.author)
        client.send_message(message.channel,
                            message.author + "{}'s balance is: {} GRLC".format(message.author, row[1]))
    def do_stats(message):
        print("Stats")

    def do_start(message):
        """
        Check if the user has enough coins to start
        :param message:
        :return:
        """

        try:
            pieces = message.content.split(' ')
            amount = float(pieces[1])
            balance = get_user(message.author)[1]
            if balance < amount:
                client.send_message("You have insufficient GRLC ({})".format(balance))
        except ValueError:
            client.send_message(message.channel, "Please specify a valid amount of GRLC")
        except IndexError:
            client.send_message(message.channel, "Usage is c!start <balance>")


    def do_accept(message):
        pieces = message.content.split(' ')
        if len(pieces) != 2:
            client.send_message(message.channel, "Usage is `c!accept @username#1234`. You must have enough coins ")

    def nop(message):
        pass

    funcs = {
        'c!addbalance': add_balance,
        'c!stats': do_stats,
        'c!address': do_addr,
        'c!balance': do_balance,
        'c!start': do_start,
        'c!accept': do_accept,
    }
    funcs.get(message.split(' ')[0], nop)(message)

    if message.content.startswith('c!help'):
        client.send_message(message.channel, 'Functions are: ' + (', '.join(funcs.keys())))
    # if message.content.startswith('!test'):
    #     print(dir)
    #     print("{}: {}".format(message.user, message.content))
    #     counter = 0
    #     tmp = await client.send_message(message.channel, 'Calculating messages...')
    #     async for log in client.logs_from(message.channel, limit=100):
    #         if log.author == message.author:
    #             counter += 1
    #
    #     await client.edit_message(tmp, 'You have {} messages.'.format(counter))
    # elif message.content.startswith('!sleep'):
    #     await asyncio.sleep(5)
    #     await client.send_message(message.channel, 'Done sleeping')


if __name__ == "__main__":
    import os

    if not os.path.exists(db_name):
        init_db()
    client.run(conf['token'])
