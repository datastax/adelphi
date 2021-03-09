import hashlib

# Imports required by the __main__ case below
import base64
import sys

def cqlAndDigest(schemaFile):
    buff = ""
    m = hashlib.sha256()
    for line in schemaFile:
        realLine = line.strip()
        if len(realLine) == 0 or realLine.isspace():
            continue
        buff += (" " if len(buff) > 0 else "") + realLine
        if realLine.endswith(';'):
            rv = buff
            buff = ""
            m.update(rv.encode('utf-8'))
            yield (rv, m.digest())


if __name__ == "__main__":
    """Preserving this for validation of the logic above"""
    for (cql, digest) in cqlAndDigest(open(sys.argv[1])):
        print("Digest: {}, CQL: {}".format(str(base64.b64encode(digest)),cql))
