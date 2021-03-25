import logging

from tests.util.schemadiff import cqlDigestGenerator
from tests.util.schema_util import get_schema

def digestSet(schemaFile):
    rv = set()
    for (_, digest) in cqlDigestGenerator(schemaFile):
        rv.add(digest)
    return rv


def logCqlDigest(schemaFile, digestSet):
    for (cql, digest) in cqlDigestGenerator(schemaFile):
        if digest in digestSet:
            log.info("Digest: {}, CQL: {}".format(digest,cql))

log = logging.getLogger('adelphi')

class ExportCqlMixin:

    # TODO: Note that we currently have to disable support for SASI indexes when creating
    # a schema since the base config for the Cassandra Docker images doesn't enable it.
    # https://github.com/datastax/adelphi/issues/105 aims to fix this problem but until
    # that's in place we simply exclude SASI indexes from testing.
    def getBaseSchemaPath(self):
        baseSchemaPath = self.basePath("base-schema.cql")
        with open(baseSchemaPath, "w") as f:
            f.write("\n\n".join(ks.export_as_string() for ks in get_schema(sasi=False).keyspaces))
        return baseSchemaPath


    def compareToReferenceCql(self, comparePath, version=None):
        referencePath = "tests/integration/resources/diff-schemas/{}.cql".format(version)
        referenceSet = digestSet(referencePath)
        compareSet = digestSet(comparePath)

        refOnlySet = referenceSet - compareSet
        if len(refOnlySet) > 0:
            log.info("Statements in reference file {} but not in compare file {}:".format(referencePath, comparePath))
            logCqlDigest(referencePath, refOnlySet)
        compareOnlySet = compareSet - referenceSet
        if len(compareOnlySet) > 0:
            log.info("Statements in compare file {} but not in reference file {}:".format(comparePath, referencePath))
            logCqlDigest(comparePath, compareOnlySet)

        self.assertEqual(referenceSet, compareSet)
