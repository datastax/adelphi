import difflib
import glob
import logging
import os
import re
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
from tests.util.schema_util import get_schema

log = logging.getLogger('adelphi')

CQL_REFERENCE_SCHEMA_PATH = "tests/integration/resources/cql-schemas/{}.cql"
CQL_REFERENCE_KS0_SCHEMA_PATH = "tests/integration/resources/cql-schemas/{}-ks0.cql"

KEYSPACE_LINE_REGEX = re.compile(r'\s*CREATE KEYSPACE IF NOT EXISTS (\w+) ')

def linesWithNewline(fpath):
    if not os.path.exists(fpath):
        print("File {} does not exist".format(fpath))
    if os.path.getsize(fpath) <= 0:
        print("File {} is empty".format(fpath))
    print("Reading lines for file {}".format(fpath))
    with open(fpath) as f:
        rv = f.readlines()
        lastLine = rv[-1]
        if not lastLine.endswith("\n"):
            rv[-1] = lastLine + "\n"
        return rv


def extractKeyspaceName(schemaPath):
    with open(schemaPath) as schemaFile:
        for line in schemaFile:
            matcher = KEYSPACE_LINE_REGEX.match(line)
            if matcher:
                return matcher.group(1)
    return None


class TestCql(SchemaTestCase):

    # ========================== Unittest infrastructure ==========================
    def setUp(self):
        super(TestCql, self).setUp()
        self.origKeyspaces = getAllKeyspaces()
        log.info("Creating schema")
        setupSchema(self.buildSchema())
        self.addCleanup(dropNewKeyspaces, self.origKeyspaces)


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
        compareLines = linesWithNewline(comparePath)
        referenceLines = linesWithNewline(referencePath)

        diffGen = difflib.unified_diff(
            compareLines,
            referenceLines,
            fromfile=os.path.abspath(comparePath),
            tofile=os.path.abspath(referencePath))

        diffEmpty = True
        for line in diffGen:
            if diffEmpty:
                print("Diff of generated file ({}) against reference file ({})".format(
                    os.path.basename(comparePath),
                    os.path.basename(referencePath)))
            diffEmpty = False
            print(line.strip())

        if not diffEmpty:
            self.fail()


    def combineSchemas(self):
        outputDirPath = self.outputDirPath(self.version)
        allOutputFileName = "{}-all".format(self.version)
        allOutputPath = self.outputDirPath(allOutputFileName)

        schemaPaths = glob.glob("{}/*/schema".format(outputDirPath))
        self.assertGreater(len(schemaPaths), 0)
        schemas = { extractKeyspaceName(p) : p for p in schemaPaths}
        sortedKeyspaces = sorted(schemas.keys())

        with open(allOutputPath, "w+") as allOutputFile:
            cqlStr = "\n\n".join(open(schemas[ks]).read() for ks in sortedKeyspaces)
            allOutputFile.write(cqlStr)

        return allOutputPath


    # ========================== Test functions ==========================
    def test_stdout(self):
        stdoutPath = self.stdoutPath(self.version)
        stderrPath = self.stderrPath(self.version)
        subprocess.run("adelphi export-cql --no-metadata > {} 2>> {}".format(stdoutPath, stderrPath), shell=True)

        self.compareToReferenceCql(
            CQL_REFERENCE_SCHEMA_PATH.format(self.version), 
            stdoutPath)


    def test_outputdir(self):
        stderrPath = self.stderrPath(self.version)
        outputDirPath = self.outputDirPath(self.version)
        os.mkdir(outputDirPath)
        subprocess.run("adelphi --output-dir={} export-cql --no-metadata 2>> {}".format(outputDirPath, stderrPath), shell=True)

        self.compareToReferenceCql(
            CQL_REFERENCE_SCHEMA_PATH.format(self.version), 
            self.combineSchemas())


    def test_some_keyspaces_stdout(self):
        stdoutPath = self.stdoutPath(self.version)
        stderrPath = self.stderrPath(self.version)
        subprocess.run("adelphi --keyspaces=my_ks_0 export-cql --no-metadata > {} 2>> {}".format(stdoutPath, stderrPath), shell=True)

        self.compareToReferenceCql(
            CQL_REFERENCE_KS0_SCHEMA_PATH.format(self.version), 
            stdoutPath)


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