from flask import Flask, request, redirect, session, url_for, render_template, send_file, abort
from flask.json import jsonify
from markupsafe import escape
from utils import *
import json
from credentials import SITE_SECRET_KEY
from dbconn import Conn
from squawker_errors import *
from serverside import *
import logging
from account import Account
from message import Message
from profile import Profile
from market import Listing

import re

app = Flask(__name__)

app.secret_key = SITE_SECRET_KEY

site_url = 'https://squawker.app'

logger = logging.getLogger('squawkerAPI_app')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='squawkerAPI_app.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
handler2 = logging.FileHandler(filename='squawkerAPI.log', encoding='utf-8', mode='a')
handler2.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler2)



@app.route("/api", methods=['GET'])
def index():
    return render_template("api.html.jinja")


@app.route('/api/v1/<call>?', methods=['GET'])
def api(call):
    '''Api Gateway Route'''
    if call in ['messages', 'profile', 'market']:
        flags = {
            "messages": 100000000,
            "profile":   50000000,
            "market":    30000000,
        }
        arguments = {'satoshis': flags[call]}
        for x in [('asset', ASSETNAME), ('count', 50), ('account', None)]:
            arguments[x[0]] = request.args.get(x[0], default=x[1])
        data = find_latest_flags(arguments)

    elif call in ['message','listing']:
        try:
            data = parse_ipfs(request.args)
        except:
            logger.info(f"encountered and error pulling ipfs")
    else:
        logger.info(f"{call} was attempted to be called against the api with args {request.args} but failed to match.")
        abort(404)
    results = {'endpoint': call, 'results': data}.update(arguments)
    return json.dumps(results)
