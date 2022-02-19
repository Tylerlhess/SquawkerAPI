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