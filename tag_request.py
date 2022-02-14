import requests, logging

logger = logging.getLogger('squawkerAPI_tag_request')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='squawkerAPI_tag_request.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


def send(url, text):
    logger.info(f"sending {url} with text {text} came from {text}")
    test = requests.post(url, json=text)
    logger.info(f"test came back {test}")
    return test.json()


def get_messages(url):
    latest = []
    logger.info(f"url = {url}")
    request = requests.get(url)
    logger.info(f"{request.text} {request.json}")
    for x in request.json():
        print(x)
        latest.append(send(url+"call=message", x))
    return latest


if __name__ == '__main__':
    address, key = "", ""
    while address == "":
        address = input("What is the ravencoin address you wish to use?")
    while key =="":
        key = input("What is the pgp public key you wish to use?")
    tagTest = {"tag_type": "AET", "ravencoin_address": address, "pgp_pubkey": key}
    print(tagTest)
    answer = requests.post("http://squawker.app:8001/api/tag?", json=tagTest).json()
    print(answer)
    signature = input(f"Please get signature of '{answer['metadata_signature']['signature_hash']}'")
    answer["metadata_signature"]["signature"] = signature
    print(answer)
    print(requests.post("http://squawker.app:8001/api/tag?", json=answer))
