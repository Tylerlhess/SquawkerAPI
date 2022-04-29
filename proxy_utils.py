import logging
from profile import Profile
from serverside import *
import json
import zlib
from hashlib import sha256
from utils import get_logger
import time
from dbconn import Conn


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
        try:
            tag = json.dumps(_text["tag"])
        except TypeError:
            logger.info(f"_text2 is {_text}")
            _text = _text.replace('\n', r'\n')
            logger.info(f"_text3 is {_text}")
            _text = json.loads(_text)
            tag = json.dumps(_text["tag"])
            logger.info(f"_text4 is {tag}")
            logger.info(f"tag encode came out to {sha256(tag.encode('utf-8')).hexdigest()}")
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
    raw_json = rvnipfs.get_json(hash)
    ordered_text = create_ordered_json(raw_json)
    logger.info(f"validate_ipfs_tag")
    return validate_tag_object(ordered_text, rvnrpc)


def create_ordered_json(raw_json: dict) -> str:
    try:
        ordered_text = '{"tag": {"tag_type": "' + raw_json['tag']['tag_type'] + '", "ravencoin_address": "' + \
                   raw_json['tag']['ravencoin_address'] + '", "pgp_pubkey": "' + raw_json['tag']['pgp_pubkey'] + \
                   '"}, "metadata_signature": {"signature_hash": "' + raw_json['metadata_signature']['signature_hash'] + \
                   '", "signature": "' + raw_json['metadata_signature']['signature'] + '"} }'
    except TypeError:
        logger.info(f"failed to parse {raw_json} recasting from a json")
        raw_json = json.loads(raw_json)
        ordered_text = '{"tag": {"tag_type": "' + raw_json['tag']['tag_type'] + '", "ravencoin_address": "' + \
                   raw_json['tag']['ravencoin_address'] + '", "pgp_pubkey": "' + raw_json['tag']['pgp_pubkey'] + \
                   '"}, "metadata_signature": {"signature_hash": "' + raw_json['metadata_signature']['signature_hash'] + \
                   '", "signature": "' + raw_json['metadata_signature']['signature'] + '"} }'

    return ordered_text


def create_tag_object(ipfs_hash: str, rvnrpc=rvn, rvnipfs=ipfs):
    if validate_ipfs_tag(ipfs_hash, rvnrpc, rvnipfs) == True:
        ordered = create_ordered_json(rvnipfs.get_json(ipfs_hash)).replace('\n', r'\n')
        _ordered = json.loads(ordered)
        logger.info(f"found order and dumped {_ordered}")
        crc32_address = zlib.crc32(_ordered['tag']['ravencoin_address'].encode('utf-8'))
        asset_string = f"PGP_{crc32_address}"
        logger.info(f"crc32 came out to {crc32_address} and asset string was {asset_string}")
        results = rvnrpc.issueunique("SQUAWKER", [asset_string], [ipfs_hash], _ordered['tag']['ravencoin_address'], "RUbMcZS36hvfj223sRpYmchY4PEbibNcCi")
        logger.info(f"The results of creating the asset SQUAWKER#{asset_string} with hash {ipfs_hash} are {results}")
        return results
    else:
        logger.info(f"{ipfs_hash} seems to not be valid.")
        return f"{ipfs_hash} seems to not be valid."


def create_kaw_hash(request: dict) -> str:
    logger.info(f"{request} made it to create_kaw_hash")
    try:
        sender = request["sender"]
    except KeyError:
        sender = request["address"]
    if "message" in request:
        try:
            media = request["media"]
        except KeyError:
            media = ""
        kaw = '{"sender": "' + sender + '", "profile": {' + '}, "timestamp": ' + str(time.time()) + ', "message": "' + request["message"] + '", "media": "[' + ",".join(media) + ']" }'
        request["hash_order"] = " ".join(["sender", "profile", "timestamp", "message", "media"])
    else:
        if "timestamp" not in request:
            request["timestamp"] = str(time.time())
            request["hash_order"] += " timestamp"
        kaw = '{' + ', '.join([f'"{key}": "{request[key]}"' for key in request["hash_order"].split()]) + '}'
    logger.info(f"raw json for create_kaw_hash {kaw}")
    hashed_kaw = sha256(kaw.encode('utf-8')).hexdigest()
    full_kaw = build_full_kaw(kaw, sender, hashed_kaw, request["hash_order"].split())
    return full_kaw


def build_full_kaw(contents: str, sender: str, kaw_hash: str, hash_order: list) -> str:
    response = '{"sender": "' + sender + '", "timestamp": ' + str(time.time()) + ', "contents": "' + contents.replace('"', '\\"') + '", "metadata_signature": "{ \\"hash_order\\": \\"' + ' '.join(hash_order) + '\\", \\"signature_hash\\": \\"' + kaw_hash + '\\", \\"signature\\": \\"\\" }"}'
    return response


def order_json(raw_json: dict) -> str:
    ordered_text = '{'
    try:
        if len(raw_json["metadata_signature"]["hash_order"]) > 0:
            ordered_text += ', '.join(['"' + key + '": "' + raw_json["contents"][key] + '"' for key in raw_json["metadata_signature"]["hash_order"].split()])
    except TypeError:
        logger.info(f"failed to parse {raw_json} recasting from a json")
        raw_json = json.loads(raw_json)
        ordered_text += ', '.join(['"' + key + '": "' + raw_json["contents"][key] + '"' for key in raw_json["metadata_signature"]["hash_order"].split()])
    except KeyError:
        logger.info(f"No hash order in the metadata signature")
        ordered_text += '"sender": "' + raw_json["contents"]["sender"] + '", \
"profile": {' + raw_json["contents"]["profile"] + '"' + '}, \
"timestamp": ' + raw_json["contents"]["timestamp"] + ', \
"message": "' + raw_json["contents"]["message"] + '", \
"media": "' + raw_json["contents"]["media"] + '"'
    ordered_text += '}'
    return ordered_text


def validate_wrap(request: str, rvnrpc=rvn) -> bool:
    text = request.replace('\n', r'\n')
    logger.info(f"trying to validate {text}")
    try:
        _text = json.loads(text)
        logger.info(f"_text is {_text}")
        contents = pull_out_contents(_text)
        logger.info(f"contents encode came out to {sha256(contents.encode('utf-8')).hexdigest()}")
        if sha256(contents.encode('utf-8')).hexdigest() == _text["metadata_signature"]["signature_hash"]:
            try:
                res = rvnrpc.verifymessage(_text["contents"]["sender"], _text["metadata_signature"]["signature"], _text['metadata_signature']['signature_hash'])['result']
            except KeyError:
                res = rvnrpc.verifymessage(_text["contents"]["address"], _text["metadata_signature"]["signature"],
                                           _text['metadata_signature']['signature_hash'])['result']

            logger.info(f"result is {res}")
            return res
        logging.info(f"{sha256(contents.encode('utf-8')).hexdigest()} != {_text['metadata_signature']['signature_hash']}")
        return False
    except KeyError as e:
        logger.info(f"Got KeyError {e} off {text}")
        raise KeyError(e)
    except TypeError as e:
        logger.info(f"Got TypeError {e} off {text}")
        raise TyperError(e)


def pull_out_contents(_text):
    try:
        logger.info(f"contents is {_text['contents']}")
        contents = _text["contents"]
        try:
            for key in ["contents", "metadata_signature"]:
                logger.info(f"trying to pull {key} out of {_text[key]}")
                # these come out as strings so should be consistent
                _text[key] = json.loads(_text[key])
        except Exception as e:
            logger.info(f"Error: {type(e)}: {str(e)}")
            raise e
    except TypeError:
        logger.info(f"_text failed _text2 is {_text}")
        _text = _text.replace('\n', r'\n')
        logger.info(f"_text3 is {_text}")
        _text = json.loads(_text)
        for key in ["contents", "metadata_signature"]:
            _text[key] = json.loads(_text[key])
        contents = json.dumps(_text["contents"])
        logger.info(f"_text4 is {contents}")
    except Exception as e:
        logger.info(f"Error: {type(e)}: {str(e)}")
        raise e
    return contents


def send_proxy_msg(msg: str, asset=ASSETNAME, address=COMMUNITY_POT, sats=0.11, rvnrpc=rvn) -> bool:
    logger.info(f"Message {msg} sending now")
    hash = ipfs.add_json(msg)
    ipfs.pin.add(hash)
    return rvnrpc.transfer(asset, sats, address, hash, 0, address, address)


def verify(request, rvnrpc=rvn):
    jsonRequest = json.loads(request.args['jsonRequest'])
    res = rvnrpc.verifymessage(jsonRequest["address"], jsonRequest["signature"], jsonRequest["signstring"])['result']
    return res


def validate_proxy(ipfs_hash, rvnrpc=rvn):
    """Ready for any message type"""
    raw_message = ipfs.cat(ipfs_hash)
    logger.info(f"raw message is {raw_message} validating")
    try:
        _text = json.loads(raw_message)
        contents = pull_out_contents(_text)
        logger.info(f"contents encode came out to {sha256(contents.encode('utf-8')).hexdigest()}")
        if sha256(contents.encode('utf-8')).hexdigest() == _text["metadata_signature"]["signature_hash"]:
            res = rvnrpc.verifymessage(_text["contents"]["sender"], _text["metadata_signature"]["signature"],
                                       _text['metadata_signature']['signature_hash'])['result']
            logger.info(f"result is {res}")
            return res
        logging.info(
            f"{sha256(contents.encode('utf-8')).hexdigest()} != {_text['metadata_signature']['signature_hash']}")
        return False
    except KeyError as e:
        logger.info(f"Got KeyError {e} off {text}")
        raise KeyError(e)
    except TypeError as e:
        logger.info(f"Got TypeError {e} off {text}")
        raise TyperError(e)

    return False


def nft_lookup(request, rvnrpc=rvn):
    nft = request.args['nft']
    res = rvnrpc.listaddressesbyasset(nft)['result']
    return res


def profile_proxy():
    pass