from serverside import *
import json
from hashlib import sha256
from ..utils import get_logger

logger = get_logger('squawker_utils')


def nft_to_address(nft: str, rvnrpc=rvn) -> str:
    return rvnrpc.listaddressesbyasset(nft)['result']


def nft_signed_message(nft: str, message: str, signature: str, rvnrpc=rvn) -> str:
    return rvnrpc.verifymessage(nft_to_address(nft, rvnrpc=rvnrpc), signature, message)['result']


def tag_object_hash(text: str) -> str:
    try:
        pydict = json.loads(text)
        for key in [
            "tag_type",
            "ravencoin_address",
            "pgp_pubkey"
        ]:
            a = pydict[key]

        r_json = '{ "tag": ' + text.replace("'",'"') + ', "metadata_signature": { "signature_hash": "' + \
                sha256(text.encode('utf-8')).hexdigest() + '", "signature": ""}}'
        return r_json
    except KeyError as e:
        raise KeyError(f"JSON was missing {e}")


def validate_tag_object(text: str, rvnrpc=rvn) -> bool:
    _text = json.loads(text)
    tag = json.dumps(_text["tag"])
    if sha256(tag.encode('utf-8')).hexdigest() == _text["metadata_hash"]["signature_hash"]:
        return rvnrpc.verifymessage(_text["tag"]["ravencoin_address"], _text["metadata_hash"]["signature_hash"], tag)
    return False

