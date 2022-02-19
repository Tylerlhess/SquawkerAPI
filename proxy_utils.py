import logging

from serverside import *
import json
from hashlib import sha256
from utils import get_logger

logger = get_logger('squawker_proxyutils')


def nft_to_address(nft: str, rvnrpc=rvn) -> str:
    return rvnrpc.listaddressesbyasset(nft)['result']


def nft_signed_message(nft: str, message: str, signature: str, rvnrpc=rvn) -> str:
    return rvnrpc.verifymessage(nft_to_address(nft, rvnrpc=rvnrpc), signature, message)['result']


def tag_object_hash(text: str) -> str:
    logger.info(f"tag_object_hash")
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
    text = text.replace('\n', r'\n')
    logger.info(f"trying to validate {text}")
    try:
        _text = json.loads(text)
        logger.info(f"_text is {_text}")
        tag = json.dumps(_text["tag"])
        if sha256(tag.encode('utf-8')).hexdigest() == _text["metadata_signature"]["signature_hash"]:
            res = rvnrpc.verifymessage(_text["tag"]["ravencoin_address"], _text["metadata_signature"]["signature"], _text['metadata_signature']['signature_hash'])['result']
            logger.info(f"result is {res}")
            return res
        logging.info(f"{sha256(tag.encode('utf-8')).hexdigest()} != {_text['metadata_signature']['signature_hash']}")
        return False
    except KeyError as e:
        logger.info(f"Got KeyError {e} off {text}")
        raise KeyError(e)

def validate_ipfs_tag(hash: str, rvnrpc=rvn, rvnipfs=ipfs) -> bool:
    raw_json = ipfs.get_json(hash)
    ordered_text = '{"tag": {"tag_type": "' + raw_json['tag']['tag_type'] + '", "ravencoin_address": "' + \
                   raw_json['tag']['ravencoin_address'] + '", "pgp_pubkey": "' + raw_json['tag']['pgp_pubkey'] + \
                   '"}, "metadata_signature": {"signature_hash": "' + raw_json['metadata_signature']['signature_hash'] +\
                   '", "signature": "' + raw_json['metadata_signature']['signature'] + '"} }'
    logger.info(f"validate_ipfs_tag")
    return validate_tag_object(ordered_text)


def create_tag_object(text: str, rvnrpc=rvn) -> bool:
    pass

