
class UserManager:
    def __init__(self, conn, grlc):
        self.conn = conn
        self.grlc = grlc

    def _get_user_from_id(self, ctx, id: int):
        """
        Useful for turning ids stored in the db back into user objects
        :param id: int
        :return:
        """
        return ctx.bot.get_user(id)

    def get_user(self, userId):
        """
        Get the user row for a given userId
        :param userId:
        :return:
        """
        c = self.conn.cursor()
        c.execute("SELECT * FROM users WHERE userId = ?", (userId,))
        user_row = c.fetchone()
        if user_row is None:
            return self.create_user(userId)
        return user_row

    def get_balance(self, userId):
        """
        Get the balance for a userId
        :param userId:
        :return:
        """
        user_row = self.get_user(userId)
        return self.grlc.get_balance(user_row[1])

    def create_user(self, userId):
        """
        Create a user in the db for a given userId
        :param userId:
        :return:
        """
        c = self.conn.cursor()
        wallet_addr = self.grlc.generate_wallet()
        c.execute("INSERT INTO users VALUES (?, ?)", (userId, wallet_addr))
        self.conn.commit()
        return self.get_user(userId)
