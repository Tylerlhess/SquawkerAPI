import logging

from flask import Flask, request, abort, redirect, url_for, session, flash
from flask.json import jsonify
from utils import *
from credentials import SITE_SECRET_KEY
from squawker_errors import *
from serverside import *
from account import Account
from api_message import Message
from profile import Profile
from market import Listing
# from flask_classful import FlaskView
from functools import wraps
from proxy_utils import validate_tag_object, tag_object_hash, validate_ipfs_tag, create_kaw_hash, validate_wrap
from proxy_utils import send_proxy_msg, verify, validate_proxy, nft_lookup
import tempfile, zlib
from dbconn import Conn

app = Flask(__name__)

app.secret_key = SITE_SECRET_KEY


site_url = 'https://squawker.app'


logger = get_logger('squawkerAPI_app')

chart = {"kaw": 0.11, "profile": 0.105}

@app.route("/", methods=['GET'])
def index():
    return "api.html.jinja"


@app.route("/api", methods=['GET','POST'])
def api():
    try:
        logger.info(f"API called with {request}: {request.args}")
        stuff = dict()
        for x in request.args:
            stuff[x] = request.args[x]
            logger.info(f"Recording request {x} as {stuff[x]}")
        if request.method == 'POST' and request.json:
            tx = request.json
            stuff["tx"] = tx
            logger.info(f"tx set to {tx} as {type(tx)} and stuff = {stuff}")
        if 'call' in stuff.keys():
            call = stuff['call']
            logger.info(f"Call in stuff")
        else:
            call = 'messages'
            logger.info(f"Call not in stuff")
        if call in ['messages', 'market', 'profile'] and request.method == 'GET':
            flags = {
                "messages": 100000000,
                "profile":   50000000,
                "market":    20000000,
            }

            arguments = {'satoshis': flags[call]}
            logger.info(f"Call is for {call} {arguments}")
            for x in [('asset', ASSETNAME), ('count', 50), ('account', None)]:
                arguments[x[0]] = request.args.get(x[0], default=x[1])
            data = find_latest_flags(**arguments)
            logger.info(f"Data came back for {call} {data}")

        if call in ['message', 'listing', 'profile']:
            try:
                data = parse_ipfs(stuff)
            except:
                logger.info(f"encountered and error pulling ipfs with {stuff}")
        elif call not in ['messages', 'profile', 'market', 'message','listing']:
            logger.info(f"{call} was attempted to be called against the api with args {request.args} but failed to match.")
            abort(404)
        if isinstance(data, list):
            return jsonify(data)
        else:
            return data.json()
    except TypeError as e:
        logger.info("got TypeError")
        raise(e)
    except Exception as e:
        logger.info(f"Error {type(e)} : {e}")
        raise(e)


@app.route('/api/tag', methods=['POST'])
def maketag():
    tag_json = request.json
    logger.info(f"tag_json came in as {tag_json}")
    text_json = json.dumps(tag_json)
    logger.info(f"text_json came in as {text_json}")
    try:
        if validate_tag_object(text_json) == True:
            logger.info(f"{tag_json} is valid. ")
            json_hash = ipfs.add_json(tag_json)
            ipfs.pin.add(json_hash)
            logger.info(validate_ipfs_tag(json_hash))
            return f"Your submission was valid. Please send one SQUAWKER/AET_REDEMPTION_TOKEN to 'RUbMcZS36hvfj223sRpYmchY4PEbibNcCi' with the IPFS message as '{json_hash}'"
        else:
            return f"Invalid Object: {text_json} hashes don't match {validate_tag_object(text_json)}"
    except KeyError:
        r_json = tag_object_hash(text_json)
        logger.info(f"tag processed as {r_json}")
        return r_json


@app.route('/api/proxy/<intent>', methods=['GET','POST'])
def send_by_proxy(intent):
    try:
        if validate_wrap(request.json):
            msg = json.loads(request.json)
            if "sender" not in msg:
                msg["sender"] = msg["address"]
            logger.info(f"Validate wrap returned true. msg is {msg}")
            try:
                conn = Conn()
                if conn.check_balance(msg["sender"]) > 0.02:
                    if conn.update_balance(msg["sender"], float(-0.02)):
                        send_proxy_msg(msg, address=msg["sender"], sats=chart[intent])
                    else:
                        raise InsufficientFunds(f"{msg['sender']} had an issue updating funds.")
                elif conn.check_balance(COMMUNITY_POT) > 0.02:
                    if conn.update_balance(COMMUNITY_POT, float(-0.02)):
                        send_proxy_msg(msg, asset=ASSETNAME, address=COMMUNITY_POT, sats=chart[intent])
                    else:
                        raise InsufficientFunds(f"{msg['sender']} had an issue updating funds.")
                else:
                    raise InsufficientFunds(f"{msg['sender']} does not have sufficient funds.")
            except InsufficientFunds as e:
                return str(e)
        else:
            logger.info(f"Validate wrap returned false.")
            return f"Incorrect signature"
    except Exception as e:
        logger.info(f"Exception thrown {e}")
        return str(e)
    logger.info(f"Send by proxy worked redirecting to home.")
    return json.dumps({"sent": True, "location": "http://squawker.app"})


@app.route('/api/proxy_sign', methods=['GET','POST'])
def sign_proxy():
    sign_request = json.loads(request.json)
    logger.info(f"sendbyproxy sign request {sign_request}")
    sign_request["hash_order"] = " ".join([key for key in sign_request])
    response = create_kaw_hash(sign_request)
    logger.info(f"sign request response {response}")
    return response


@app.route('/api/verify_sig', methods=['POST'])
def verify_sig():
    logger.info(f"Verify request for, {request.args}")
    res = verify(request)
    logger.info(f"Result is {res}")
    return f"Result is {res}"


@app.route('/api/verify_proxied', methods=['POST'])
def verify_proxied():
    logger.info(f"Verify proxy request for, {request.args}")
    res = validate_proxy(request.args["ipfs_hash"])
    logger.info(f"Result is {res}")
    return f"Result is {res}"


@app.route('/api/nft_lookup', methods=['POST', 'GET'])
def nft_lookups():
    logger.info(f"NFT lookup, {request.args}")
    res = nft_lookup(request)
    logger.info(f"Result is {res}")
    return f"{res}"


def parse_ipfs(data):
    kaw = None
    try:
        logger.info(f"{data} sent for data {data['call']}")
        data = data

        if 'message' in data['call']:
            logger.info(f"matched on message {data['tx']} {type(data['tx'])}")
            kaw = Message(data['tx'])
        if data['call'] == "listing":
            kaw = Listing(data['tx'])
        if data['call'] == "profile":
            logger.info(f"matched on message {data['tx']} {type(data['tx'])}")
            kaw = Profile(data['tx']['address'][0])
        logger.info(f"message returned as {kaw.__str__()}")

    except Exception as e:
        logger.info(f"{type(e)} {e}")
        raise e
    logger.info(f"Kaw is {kaw}")
    return kaw




