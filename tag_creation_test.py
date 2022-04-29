from proxy_utils import create_tag_object
from serverside import *

ASSET_NAME = "SQUAWKER/AET_REDEMPTION_TOKEN"

#search for transfers of 1 to RUbMcZS36hvfj223sRpYmchY4PEbibNcCi
utxos = rvn.getaddressutxos({"addresses": ["RUbMcZS36hvfj223sRpYmchY4PEbibNcCi"], "assetName": ASSET_NAME})['result']
viable_tags = []
for x in utxos:
    if x["satoshis"] == 100000000:
        print(x['txid'])
        raw_txid = rvn.decoderawtransaction(rvn.getrawtransaction(x['txid'])['result'])['result']
        print(raw_txid)
        for y in raw_txid['vout']:
            vout = y["scriptPubKey"]
            if vout["type"] == "transfer_asset" and vout["asset"]["name"] == ASSET_NAME and vout["asset"][
                "amount"] == 1:
                kaw = {
                    "address": vout["addresses"],
                    "message": vout["asset"]["message"],
                    "block": raw_txid["locktime"]
                }
                viable_tags.append(kaw)
print(viable_tags)
for tag in viable_tags:
    print(create_tag_object(tag['message']))

