from serverside import *
import logging
from hashlib import sha256
import json
from flask import Flask, request, abort, redirect, url_for, session, flash
from functools import wraps


logger = logging.getLogger('squawker_utils')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='squawker_utils.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
handler2 = logging.FileHandler(filename='squawker.log', encoding='utf-8', mode='a')
handler2.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler2)

debug = 0


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


def get_logger(logger_name: str, app_name='squawker') -> logging:
    new_logger = logging.getLogger(logger_name)
    new_logger.setLevel(logging.DEBUG)
    new_handler = logging.FileHandler(filename=logger_name+'.log', encoding='utf-8', mode='a')
    new_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    new_logger.addHandler(new_handler)
    new_handler2 = logging.FileHandler(filename=app_name+'.log', encoding='utf-8', mode='a')
    new_handler2.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    new_logger.addHandler(new_handler2)
    return new_logger


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if not session["address"]:
            flash("You need to login", "warning")
            redirect(url_for('login'))

        return f(*args, **kwargs)

    return decorated_function