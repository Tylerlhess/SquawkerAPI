import json
from flask.json import jsonify
import requests, logging
from serverside import rvn
from credentials import USER, PASSWORD
from requests.auth import HTTPBasicAuth


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
    logger.info(f"url = {url}")
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

    tagTest = { "tag_type": "AET", "ravencoin_address": "RUbMcZS36hvfj223sRpYmchY4PEbibNcCi", "pgp_pubkey": "-----BEGIN PGP PUBLIC KEY BLOCK-----\nVersion: GnuPG v1\n\nmQENBGFLr7QBCAC1WrD7wYvWC8E9zqwcLOiw4wf5bY67/VNaekbPu9hxR1k5Hud9\nTjSbIRw4teMxtc6b2G4AdiY/2ByY43dxSSFueTyV9x1SiV61sOH0RbMZn00I5CSF\nBXlGgCPjfaC3dY4DKIpfhjw1eoMz8CuTOvz4K0KiZ8ac9yFSc4NjxW2Vr+uOaUmK\nGwkDVpplxHnKb2VYdHLaN7n8CKhUPtpUM5E70Xsp9QQimCnJOVZIaTZA1t8G/GeD\nQik9ZTbczu7yfQj3wWDp9m0j8k9HTM61cYh78t5IdlsLcBBCn5wdOw2Uc/Dgt6uo\nevmDW4uMzNQXgEFpseuNlFpTNLw/UxjLv0RBABEBAAG0MVR5bGVyIEhlc3MgKEkg\nYW0gQmFkZ3V5dHkpIDx0eWxlcmxoZXNzQGdtYWlsLmNvbT6JATgEEwECACIFAmFL\nr7QCGwMGCwkIBwMCBhUIAgkKCwQWAgMBAh4BAheAAAoJEH55+QGc03NKTs4IAIPQ\nYu/i7GX2ZG1dTdWHvGxJDJd9AzuLTkMHHbm7YHCPQHLe9GiKsCNsYAXPPwJRvheH\n4rsdNW1cvHT4+7fvPS8ouo+molpK4PBgwTsVApnwmufIb/xH8A0rds3y8cNldSl9\np/ewYuxhu3wyUIknRz3K71bbG/+JmTQQxJKMVRfXgYBDHkmWmzCmeQXl++6keYZQ\n38Yhk+hXDIwHnQCoc7fB9EbHup8XLJ/L9um+07FinSiicKgYV5chFiQPR+0mPBW1\n5YLIycwkbG7Ba2NMwVGgEDjKsEErvHDtvjym6C9tMd6kswK7ly/Ha4ftMPDjs5Lo\nwVs33DXATrMPxGUHSRa5AQ0EYUuvtAEIALrohb2W/toVsHs49ucalNJyO6oiXmQ8\n+AcYYLDIxtYcAp5YJ0Bbs2k2nrVMOzZe3ll2H9JA3BeMdQC+By0V1ViK5vk9K0SI\ny5aLqUvnU5ZPGE3x+gVc8F+uDFRst9uG0j8ZFa1aByksRi6rn5BcWpCbqR9HLsng\nQDtHKA/kF9Ae4GN2J7Fjch6KteUcv4LMfwilHCXA/jpAgf4zjfpM7QWZ13bdUvq8\nhYgcNZPDfEW1KSoeN0lmsLiVMv0d67oyZO7etalL0gnfyZ97lUBxlAfzM/LoMOZl\nr+UWqkELTJP7ZCIbWT+bqkjQa3Ql3nlOCjfDPY3C8yuKXG8B35vmoREAEQEAAYkB\nHwQYAQIACQUCYUuvtAIbDAAKCRB+efkBnNNzSoCdCACS+Jfj9Tjoe2Y3VoV+QQ3c\nkRDpHvMZdVoSohvPuCNnW0SjKvpYqjqVaz+2IRCSS8qYz/B3gJxFR5hDlTS4REep\nFof0HupDT4XQ5OzdIXIIN0sZwrrn6cOqYexBqz6Of8m4gInGOEwwU4gfDdL4ZvfN\n10bUBfaERZsf4/tYJtXBnlDA56PBXF++npJ9ApUZ+T9I/CWDQuYzTsCjSoT+dgSL\n6kL5PFnM60nLfiZXzWKMmw/pgel1s2Oc1TbTWYqUE6A5XJqpsiHGiAXfK98joCyW\n5/2a0wWZhJOoDXKS7U2cpa0A0zj6I08OwkMKANg8/kwBDv2xZO0ME3i7FGac6qlr\n=Uah0\n-----END PGP PUBLIC KEY BLOCK-----"}
    print(tagTest)
    answer = requests.post("http://squawker.app:8001/api/tag?", json=tagTest).json()
    print(answer)
    sig2 = requests.post("http://127.0.0.1:8766", data='{"jsonrpc": "1.0", "id":"curltest", "method": "signmessage", "params": ["' + answer["tag"]["ravencoin_address"] + '", "' + answer["metadata_signature"]["signature_hash"] + '"] }', headers={"content_type": "text/plain"}, auth=HTTPBasicAuth(USER, PASSWORD))
    #myusername - -data - binary \'{"jsonrpc": "1.0", "id":"curltest", "method": "signmessage", "params": ["1D1ZrZNe3JUo7ZycKEYQQiQAWd9y54F4XX", "my message"] }\' -H \'content-type: text/plain;\' /
    print(sig2.json())
    answer["metadata_signature"]["signature"] = sig2.json()["result"]
    print(answer)
    print(requests.post("http://squawker.app:8001/api/tag?", json=answer))
