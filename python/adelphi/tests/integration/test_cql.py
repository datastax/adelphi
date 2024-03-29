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

from tests.integration import SchemaTestCase, setupSchema, getAllKeyspaces, dropNewKeyspaces
from tests.util.schemadiff import cqlDigestGenerator
from tests.util.schema_util import get_schema

log = logging.getLogger('adelphi')

CQL_REFERENCE_SCHEMA_PATH = "tests/integration/resources/cql-schemas/{}.cql"
CQL_REFERENCE_KS0_SCHEMA_PATH = "tests/integration/resources/cql-schemas/{}-ks0.cql"

def digestSet(schemaFile):
    rv = set()
    for (_, digest) in cqlDigestGenerator(schemaFile):
        rv.add(digest)
    return rv


def logCqlDigest(schemaFile, digestSet):
    for (cql, digest) in cqlDigestGenerator(schemaFile):
        if digest in digestSet:
            log.info("Digest: {}, CQL: {}".format(digest,cql))


class TestCql(SchemaTestCase):

    # ========================== Unittest infrastructure ==========================
    def setUp(self):
        super(TestCql, self).setUp()
        self.origKeyspaces = getAllKeyspaces()
        log.info("Creating schema")
        setupSchema(self.buildSchema())


    def tearDown(self):
        super(TestCql, self).tearDown()
        dropNewKeyspaces(self.origKeyspaces)


    # ========================== Helper functions ==========================
    # TODO: Note that we currently have to disable support for SASI indexes when creating
    # a schema since the base config for the Cassandra Docker images doesn't enable it.
    # https://github.com/datastax/adelphi/issues/105 aims to fix this problem but until
    # that's in place we simply exclude SASI indexes from testing.
    def buildSchema(self):
        baseSchemaPath = self.basePath("base-schema.cql")
        with open(baseSchemaPath, "w") as f:
            f.write("\n\n".join(ks.export_as_string() for ks in get_schema(sasi=False).keyspaces))
        return baseSchemaPath


    def compareToReferenceCql(self, referencePath, comparePath):
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


    # ========================== Test functions ==========================
    def test_stdout(self):
        stdoutPath = self.stdoutPath(self.version)
        stderrPath = self.stderrPath(self.version)
        subprocess.run("adelphi export-cql --no-metadata > {} 2>> {}".format(stdoutPath, stderrPath), shell=True)

        self.compareToReferenceCql(
            CQL_REFERENCE_SCHEMA_PATH.format(self.version), 
            self.stdoutPath(self.version))


    def test_outputdir(self):
        stderrPath = self.stderrPath(self.version)
        outputDirPath = self.outputDirPath(self.version)
        os.mkdir(outputDirPath)
        subprocess.run("adelphi --output-dir={} export-cql --no-metadata 2>> {}".format(outputDirPath, stderrPath), shell=True)

        # Basic idea here is to find all schemas written to the output dir and aggregate them into a single schema
        # file.  We then compare this aggregated file to the reference schema.  Ordering is important here but
        # the current keyspace names hash to something that causes individual keyspaces to be discovered in the
        # correct order.
        outputDirPath = self.outputDirPath(self.version)
        allOutputFileName = "{}-all".format(self.version)
        allOutputPath = self.outputDirPath(allOutputFileName)

        outputSchemas = glob.glob("{}/*/schema".format(outputDirPath))
        self.assertGreater(len(outputSchemas), 0)
        with open(allOutputPath, "w+") as allOutputFile:
            for outputSchema in outputSchemas:
                with open(outputSchema) as outputSchemaFile:
                    shutil.copyfileobj(outputSchemaFile, allOutputFile)
                    allOutputFile.write("\n")
        self.compareToReferenceCql(
            CQL_REFERENCE_SCHEMA_PATH.format(self.version), 
            allOutputPath)


    def test_some_keyspaces_stdout(self):
        stdoutPath = self.stdoutPath(self.version)
        stderrPath = self.stderrPath(self.version)
        subprocess.run("adelphi --keyspaces=my_ks_0 export-cql --no-metadata > {} 2>> {}".format(stdoutPath, stderrPath), shell=True)

        self.compareToReferenceCql(
            CQL_REFERENCE_KS0_SCHEMA_PATH.format(self.version), 
            self.stdoutPath(self.version))


    def test_some_keyspaces_outputdir(self):
        stderrPath = self.stderrPath(self.version)
        outputDirPath = self.outputDirPath(self.version)
        os.mkdir(outputDirPath)
        subprocess.run("adelphi --output-dir={} --keyspaces=my_ks_0 export-cql --no-metadata 2>> {}".format(outputDirPath, stderrPath), shell=True)

        outputDirPath = self.outputDirPath(self.version)
        outputSchemas = glob.glob("{}/*/schema".format(outputDirPath))
        self.assertEqual(len(outputSchemas), 1)
        self.compareToReferenceCql(
            CQL_REFERENCE_KS0_SCHEMA_PATH.format(self.version), 
            outputSchemas[0])


if __name__ == '__main__':
    unittest.main()