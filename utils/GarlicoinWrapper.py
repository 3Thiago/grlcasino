from jsonrpc_requests import Server

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
        addr = self.srv.getaddressesbyaccount(userId)[0]
        if addr == []:
            return self.generate_address(userId)
        
    def generate_address(self, userId):
        return self.srv.getnewaddress(userId)

    def get_balance(self, userId):
        return self.srv.getbalance(userId)
        
    def transfer(self, userIdSrc, grlcDest, amount):
        return self.srv.sendfrom(userIdSrc, grlcDest, amount)

    def move_between_accounts(self, userIdSrc, userIdDest, amount):
        return self.srv.move(userIdSrc, userIdDest, amount)
