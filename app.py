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
from proxy_utils import validate_tag_object, tag_object_hash


app = Flask(__name__)

app.secret_key = SITE_SECRET_KEY


site_url = 'https://squawker.app'


logger = get_logger('squawkerAPI_app')


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


@app.route('/tag', methods=['POST'])
def maketag():
    tag_json = request.json
    logger.info(f"tag_json cam in as {tag_json}")
    text_json = json.dumps(tag_json)
    try:
        if validate_tag_object(text_json):
            logger.info(f"{tag_json} is valid. ")
            return "200"
        else:
            return f"Invalid Object: {validate_tag_object(text_json)}"
    except KeyError:
        r_json = tag_object_hash(text_json)
        logger.info(f"tag processed as {r_json}")
        return r_json


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


