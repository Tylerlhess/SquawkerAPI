from serverside import *
import logging

logger = logging.getLogger('squawker_utils')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='squawker_utils.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

debug = 0


class Kaw:
    def __init__(self, tx):
        self.tx = tx
        self.t = ""

    def report(self):
        return f"{self.t} {self.__str__()}"


def tx_to_self(tx, size=1, rvnrpc=rvn):
    messages = dict()
    messages["addresses"] = [tx["address"]]
    messages["assetName"] = tx["assetName"]
    deltas = rvnrpc.getaddressdeltas(messages)["result"]
    neg_delta = [(a["satoshis"], a["address"]) for a in deltas if a["txid"] == tx["txid"] and a["satoshis"] < -((size * 100000000)-1)]
    return len(neg_delta)


def find_latest_flags(asset=ASSETNAME, satoshis=100000000, count=50, account=None, rvnrpc=rvn):
    latest = []
    logger.info(f"asset is {asset}")
    messages = dict()
    if account:
        if isinstance(account, list):
            messages["addresses"] = account
        else:
            messages["addresses"] = [account,]
    else:
        messages["addresses"] = list(rvnrpc.listaddressesbyasset(asset, False)["result"])
    messages["assetName"] = asset
    deltas = rvnrpc.getaddressdeltas(messages)["result"]
    for tx in deltas:
        if tx["satoshis"] == satoshis and tx_to_self(tx):
            transaction = rvnrpc.decoderawtransaction(rvnrpc.getrawtransaction(tx["txid"])["result"])["result"]
            for vout in transaction["vout"]:
                vout = vout["scriptPubKey"]
                if vout["type"] == "transfer_asset" and vout["asset"]["name"] == asset and vout["asset"]["amount"] == satoshis/100000000:
                    kaw = {
                        "address": vout["addresses"],
                        "message": vout["asset"]["message"],
                        "block": transaction["locktime"]
                    }
                    latest.append(kaw)
    return sorted(latest[:count], key=lambda message: message["block"], reverse=True)


def transaction_scriptPubKey(tx_id, vout, rvnrpc=rvn):
    tx_data = rvnrpc.decoderawtransaction(rvnrpc.gettransaction(tx_id)['result']['hex'])['result']
    issued_scriptPubKey = tx_data['vout'][vout]['scriptPubKey']['hex']
    return issued_scriptPubKey




