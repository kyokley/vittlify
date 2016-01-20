import os
from binascii import hexlify

def getSomewhatUniqueID(numBytes=4):
    return hexlify(os.urandom(numBytes))
