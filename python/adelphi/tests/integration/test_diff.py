import glob
import logging
import os
import shutil
import sys

try:
    import unittest2 as unittest
except ImportError:
    import unittest

if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as subprocess
else:
    import subprocess

from tests.integration import SchemaTestMixin
from tests.util.schema_util import get_schema
from tests.util.schemadiff import cqlDigestGenerator

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

class TestDiff(unittest.TestCase, SchemaTestMixin):

    def setUp(self):
        super(TestDiff, self).setUp()


    # TODO: Note that we currently have to disable support for SASI indexes when creating
    # a schema since the base config for the Cassandra Docker images doesn't enable it.
    # https://github.com/datastax/adelphi/issues/105 aims to fix this problem but until
    # that's in place we simply exclude SASI indexes from testing.
    def getBaseSchemaPath(self):
        baseSchemaPath = self.basePath("diff-base-schema.cql")
        with open(baseSchemaPath, "w") as f:
            f.write("\n\n".join(ks.export_as_string() for ks in get_schema(sasi=False).keyspaces))
        return baseSchemaPath


    def runAdelphi(self, version=None):
        exportCmd = "export-cql --no-metadata"
        stdoutPath = self.stdoutPath(version)
        stderrPath = self.stderrPath(version)
        subprocess.run("adelphi {} > {} 2>> {}".format(exportCmd, stdoutPath, stderrPath), shell=True)
        outputDirPath = self.outputDirPath(version)
        os.mkdir(outputDirPath)
        subprocess.run("adelphi --output-dir={} {} 2>> {}".format(outputDirPath, exportCmd, stderrPath), shell=True)


    def _compareToReference(self, comparePath, version=None):
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


    def evalAdelphiOutput(self, version=None):

        # Compare process for stdout
        self._compareToReference(self.stdoutPath(version), version)

        # Compare process for output dir
        outputDirPath = self.outputDirPath(version)
        allOutputFileName = "{}-all".format(version)
        allOutputPath = self.outputDirPath(allOutputFileName)

        outputSchemas = glob.glob("{}/*/schema".format(outputDirPath))
        self.assertGreater(len(outputSchemas), 0)
        with open(allOutputPath, "w+") as allOutputFile:
            for outputSchema in outputSchemas:
                with open(outputSchema) as outputSchemaFile:
                    shutil.copyfileobj(outputSchemaFile, allOutputFile)
                    allOutputFile.write("\n")
        self._compareToReference(allOutputPath, version)
