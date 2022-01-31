import json
from flask.json import jsonify
import requests, logging


logger = logging.getLogger('squawkerAPI_test')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='test.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
handler2 = logging.FileHandler(filename='squawkerAPI.log', encoding='utf-8', mode='a')
handler2.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler2)


def send(url, text):
    logger.info(f"sending {url} with text {text} came from {text}")
    test = requests.post(url, json=text)
    logger.info(f"test came back {test}")
    return test.json()


def get_messages(url):
    latest = []
    request = requests.get(url)
    logger.info(f"{request.text} {request.json}")
    for x in request.json():
        print(x)
        latest.append(send(url+"call=message", x))
    return latest


if __name__ == '__main__':
    print(get_messages("http://squawker.app:8001/api?"))
    print(requests.get("http://squawker.app:8001/api?call=market").json())
    profiles = [x for x in requests.get("http://squawker.app:8001/api?call=profile").json()]
    for profile in profiles:
        print(profile)
        print(requests.post("http://squawker.app:8001/api?call=profile", json=profile).json())
