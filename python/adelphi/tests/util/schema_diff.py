import base64
import hashlib

# Imports required by the __main__ case below
import sys

def cqlDigestGenerator(schemaPath):
    buff = ""
    with open(schemaPath) as schema:
        for line in schema:
            realLine = line.strip()
            if len(realLine) == 0 or realLine.isspace():
                continue
            buff += (" " if len(buff) > 0 else "")
            buff += realLine
            if buff.endswith(';'):
                m = hashlib.sha256()
                m.update(buff.encode('utf-8'))
                # We want to return a string containing the base64 representation
                # so that the user doesn't have to mess around with bytestrings
                yield (base64.b64encode(m.digest()).decode('utf-8'), buff)
                buff = ""


if __name__ == "__main__":
    """Preserving this for validation of the logic above"""
    for (digest, cql) in cqlDigestGenerator(sys.argv[1]):
        print("Digest: {}, CQL: {}".format(digest,cql))
