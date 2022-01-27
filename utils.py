from serverside import *
import logging
import json


logger = logging.getLogger('squawker_utils')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='squawker_utils.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

debug = 0

def tx_to_self(tx, size=1):
    messages = dict()
    messages["addresses"] = [tx["address"]]
    messages["assetName"] = tx["assetName"]
    deltas = rvn.getaddressdeltas(messages)["result"]
    neg_delta = [(a["satoshis"], a["address"]) for a in deltas if a["txid"] == tx["txid"] and a["satoshis"] < -((size * 100000000)-1)]
    return len(neg_delta)


def find_latest_flags(asset=ASSETNAME, satoshis=100000000, count=50, account=None):
    latest = []
    logger.info(f"asset is {asset}")
    messages = dict()
    if account:
        if isinstance(account, list):
            messages["addresses"] = account
        else:
            messages["addresses"] = [account,]
    else:
        messages["addresses"] = list(rvn.listaddressesbyasset(asset, False)["result"])
    messages["assetName"] = asset
    deltas = rvn.getaddressdeltas(messages)["result"]
    for tx in deltas:
        if tx["satoshis"] == satoshis and tx_to_self(tx):
            transaction = rvn.decoderawtransaction(rvn.getrawtransaction(tx["txid"])["result"])["result"]
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


def transaction_scriptPubKey(tx_id, vout):
    tx_data = rvn.decoderawtransaction(rvn.gettransaction(tx_id)['result']['hex'])['result']
    issued_scriptPubKey = tx_data['vout'][vout]['scriptPubKey']['hex']
    return issued_scriptPubKey


def parse_ipfs(data):
    raw_message = ''
    try:
        raw_message = json.dumps(json.loads(data))
        logger.info(f"raw message returned as {raw_message}")

    except:
        pass
