import subprocess
import json


class GarlicoinWrapper:
    def __init__(self, exe):
        self.garlicoin_cli = exe

    def _get_cmd(self, cmds: list):
        return subprocess.check_output([self.garlicoin_cli] + cmds).decode('utf-8').strip()

    def generate_wallet(self):
        return self._get_cmd(['getnewaddress'])

    def get_balance(self, userGrlc):
        return self._get_cmd(['getbalance', userGrlc])

    def transfer(self, grlcSrc, grlcDest, amount):
        return self._get_cmd(['sendtoaddress', grlcDest, amount, "grlcasino", "grlcasino"])
