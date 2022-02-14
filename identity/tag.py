import json

from flask import request
from flask_classful import FlaskView
from utils import login_required, get_logger
from proxy_utils import tag_object_hash, validate_tag_object

logger = get_logger("tag")


class TagView(FlaskView):

    @login_required
    def post(self):
        tag_json = request.json
        logger.info(f"tag_json cam in as {tag_json}")
        text_json = json.dumps(tag_json)
        if validate_tag_object(text_json):
            logger.info(f"{tag_json} is valid. ")
            return 200
        r_json = tag_object_hash(text_json)
        logger.info(f"tag processed as {r_json}")
        return r_json
