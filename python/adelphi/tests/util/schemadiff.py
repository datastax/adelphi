import base64
import hashlib
import logging

# Imports required by the __main__ case below
import sys

def cqlDigestGenerator(schemaFile):
    buff = ""
    for line in open(schemaFile):
        realLine = line.strip()
        if len(realLine) == 0 or realLine.isspace():
            continue
        buff += (" " if len(buff) > 0 else "")
        buff += realLine
        if realLine.endswith(';'):
            cqlStmt = buff
            buff = ""
            m = hashlib.sha256()
            m.update(cqlStmt.encode('utf-8'))
            yield (cqlStmt, base64.b64encode(m.digest()).decode('utf-8'))


if __name__ == "__main__":
    """Preserving this for validation of the logic above"""
    for (cql, digest) in cqlDigestGenerator(sys.argv[1]):
        print("Digest: {}, CQL: {}".format(digest,cql))
