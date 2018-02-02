from jsonrpc_requests import Server, jsonrpc
import json

"""
garlicoin-cli wrapper functions for:

    getaccountaddress "account"
    getaddressesbyaccount "account"
    getbalance ( "account" minconf include_watchonly )
    getnewaddress ( "account" )
    getreceivedbyaccount "account" ( minconf )
    listaccounts ( minconf include_watchonly)
    listreceivedbyaccount ( minconf include_empty include_watchonly)
    listtransactions ( "account" count skip include_watchonly)
    move "fromaccount" "toaccount" amount ( minconf "comment" )
    sendfrom "fromaccount" "toaddress" amount ( minconf "comment" "comment_to" )
    settxfee amount
"""


class GarlicoinWrapper:
    def __init__(self, rpcUrl, rpcUser, rpcPass):
        self.srv = Server(rpcUrl, auth=(rpcUser, rpcPass))

    def get_user_address(self, userId):
        addresses = self.srv.getaddressesbyaccount(str(userId))
        if not addresses:
            return self.generate_address(str(userId))
        else:
            return addresses[0]

    def generate_address(self, userId):
        return self.srv.getnewaddress(str(userId))

    def get_balance(self, userId):
        return self.srv.getbalance(str(userId))

    def transfer(self, userIdSrc, grlcDest, amount):
        return self.srv.sendfrom(str(userIdSrc), grlcDest, amount)

    def move_between_accounts(self, userIdSrc, userIdDest, amount):
        try:
            return self.srv.move(str(userIdSrc), str(userIdDest), round(amount, 8))
        except jsonrpc.TransportError as e:
            err = json.loads(e.server_response.content)['error']['message']
            msg = f"{ctx.author.mention} ERROR: {err}: {e.request.body['params']}"
            return msg
