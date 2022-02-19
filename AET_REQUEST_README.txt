To have an AET tag generated for you, you will need the following
1. One SQUAWKER/AET_REDEMPTION_TOKEN
2. PGP_key public and private - Optional if you don't provide one, one will be made for you and left in the folder this is run from.
3. Wallet that can sign transactions for the address you want the AET sent to.
4. A specific address that you will use going forward to receive encrypted content and NFTs at.

This address will also be the one used by Squawker to show your identity and keep all your communications at. There is no limit to the number of Squawker users you create but to gain reputation and followers it is best to limit the account counts.

Step 1. Acquire your supply list.
Step 2. obtain a copy of the following python script (requires having the requests lib) You can copy from here and paste into a text file saved as script_name.py

------------------------------------------------------------------------------------------------------------------------
import requests, re, pgpy
from pgpy.constants import PubKeyAlgorithm, KeyFlags, HashAlgorithm, SymmetricKeyAlgorithm, CompressionAlgorithm
from pgpy import PGPKey, PGPUID

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'


def validate(email: str) -> str:
    if re.fullmatch(regex, email):
        return email
    else:
        return ""


def create_key():
    new_key = PGPKey.new(PubKeyAlgorithm.RSAEncryptOrSign, 4096)
    name, comment, email = "", "", ""
    while name == "":
        name = input("Name: ")
    comment = input("Comment: ")
    while email == "":
        email = validate(input("Email Address: "))
        if email == "":
            print("Invalid Email Address")

    uid = PGPUID.new(name, comment=comment, email=email)
    new_key.add_uid(uid, usage={KeyFlags.Sign, KeyFlags.EncryptCommunications, KeyFlags.EncryptStorage},
                hashes=[HashAlgorithm.SHA256, HashAlgorithm.SHA384, HashAlgorithm.SHA512, HashAlgorithm.SHA224],
                ciphers=[SymmetricKeyAlgorithm.AES256, SymmetricKeyAlgorithm.AES192, SymmetricKeyAlgorithm.AES128],
                compression=[CompressionAlgorithm.ZLIB, CompressionAlgorithm.BZ2, CompressionAlgorithm.ZIP,
                             CompressionAlgorithm.Uncompressed])

    with open("pgp_private.key", "w") as pk:
        pk.write(str(new_key))
    with open("pgp_public.key", "w") as pbk:
        pbk.write(str(new_key.pubkey))
    return str(new_key.pubkey)


if __name__ == '__main__':
    address, key = "", ""
    while address == "":
        address = input("What is the ravencoin address you wish to use?")
    while key == "":
        key = input("What is the pgp public key you wish to use?(Enter to generate a new one)").replace(r'\n', '\n')
        if key == "":
            key = create_key()
            print("Your keys are in this directory save them in a safe place.")

    tagTest = {"tag_type": "AET", "ravencoin_address": address, "pgp_pubkey": key}
    answer = requests.post("http://squawker.app:8001/api/tag?", json=tagTest).json()
    signature = input(f"Please get signature of '{answer['metadata_signature']['signature_hash']}' using the wallet from resource 3")
    answer["metadata_signature"]["signature"] = signature
    print("\r\nThe json being used to create the IPFS hash is \r\n{}\r\n".format(answer))
    print(requests.post("http://squawker.app:8001/api/tag?", json=answer).text)

--------------------------------------------------------------------------------------------------------------
Step 3. Run the script using the address and PGP publickey.
Step 4. Sign the message that you are given during the script with your wallet.
Step 5. At the end of the script execution you will see a statement like
"Your submission was valid. Please send 1 SQUAWKER/AET_REDEMPTION_TOKEN to 'RUbMcZS36hvfj223sRpYmchY4PEbibNcCi' with the Memo as 'QmfNELEAypbwoVZfM9bJoBDNp4ovGeActfgeTeUeJX52N1'"
The Memo will be used in step 10

Step 6. Open your wallet and go to Transfer Asset.
Step 7. Select "SQUAWKER/AET_REDEMPTION_TOKEN" as the asset to transfer.
Step 8. For Pay to enter 'RUbMcZS36hvfj223sRpYmchY4PEbibNcCi'
Step 9. For Amount enter 1
Step 10. For Memo enter the memo from step 3
******IMPORTANT*****
Failure to attach the correct memo will cause the verification on the tag to FAIL or the tag to be generated for the WRONG ADDRESS if the memo is for a different address than the one intended.
**********************
Step 11. Click Send
Step 12. Wait for your tag to be generated to your address. This will take at least 30 blocks or more.

If you have questions or concerns please email tyler@badguyty.com
