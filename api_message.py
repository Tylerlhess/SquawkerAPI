from serverside import *
import json
import squawker_errors
import logging

logger = logging.getLogger('squawker_message')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='squawker_message.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
handler2 = logging.FileHandler(filename='squawker.log', encoding='utf-8', mode='a')
handler2.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler2)


class Message():
    def __init__(self, tx):
        # tx is { address, message, block }
        logger.info(f"tx sent in {tx}")
        if isinstance(tx, dict):
            self.tx = tx
        else:
            self.tx = json.loads(tx)
        try:
            self.raw_message = self.get_raw_message()
            self.text = self.raw_message["message"]
            self.sender = self.tx["address"]
        except:
            raise squawker_errors.NotMessage(f"Something happened in ipfshash {tx['message']}")

    def get_raw_message(self):
        try:
            ipfs_hash = self.tx["message"]
            raw_message = json.loads(ipfs.cat(ipfs_hash))
            return raw_message
        except squawker_errors.NotMessage as e:
            raise squawker_errors.NotMessage(str(e))
        except Exception as e:
            #print(type(e), e)
            pass

    def __str__(self):
        return f"""{self.sender} {self.text}"""

    def html(self):
        return {"sender": self.sender, "text": self.text}

    def json(self):
        return {'text': self.text, 'sender': self.sender}



