# SquawkerAPI
A stand alone api that can be deployed and used to grant read access on the squawker data on the blockchain.


# Test URL
'http://squawker.app:8001/api?'


# parameters
* call = ['messages', 'market', 'profile', 'message', 'listing']
* asset = any asset name
* count = count


# posting jsons
applicable calls = ['profile', 'message', 'listing']
required json attributes = ['address', 'message']

# Test script
json_test_injector.py


# Future improvements
proxy posting endpoint



