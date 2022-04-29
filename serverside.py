from ravenrpc import Ravencoin
import ipfshttpclient
from credentials import USER, PASSWORD

try:
    rvn = Ravencoin(USER, PASSWORD, port=8766)
    rvn.getblockchaininfo()
except:
    if not rvn:
        rvn = None
    print("rvn not defined")


try:
    ipfs = ipfshttpclient.connect()
except:
    ipfs = None

ASSETNAME = "SQUAWKER"
IPFSDIRPATH = "/opt/squawker/ipfs"
WALLET_ADDRESS = ""
COMMUNITY_POT = "RMFRzEJrtt6EiFgBNJugLXLEx6PU2z5rYn"


