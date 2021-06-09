import glob
import logging
import os
import sys
import yaml

if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as subprocess
else:
    import subprocess

from tests.integration import SchemaTestMixin

log = logging.getLogger('adelphi')

NB_SCHEMA_PATH = "tests/integration/resources/nb-base-schema.cql"
NB_REFERENCE_SCHEMA_PATH = "tests/integration/resources/nb-schemas/{}.yaml"

class TestNb(SchemaTestMixin):

    # ========================== Unittest infrastructure ==========================
    def setUp(self):
        super(TestNb, self).setUp()
        self.baseTestSetup()
        self.setupSchema(NB_SCHEMA_PATH)


    def tearDown(self):
        super(TestNb, self).tearDown()
        self.baseTestTeardown()


    # ========================== Helper functions ==========================
    def compareToReferenceYaml(self, comparePath, version=None):
        referencePath = NB_REFERENCE_SCHEMA_PATH.format(version)
        # Loader specification here to avoid a deprecation warning... see https://msg.pyyaml.org/load
        referenceYaml = yaml.load(open(referencePath), Loader=yaml.FullLoader)
        compareYaml = yaml.load(open(comparePath), Loader=yaml.FullLoader)
        self.assertEqual(referenceYaml, compareYaml)


    # ========================== Test functions ==========================
    def test_stdout(self):
        stdoutPath = self.stdoutPath(self.version)
        stderrPath = self.stderrPath(self.version)
        subprocess.run("adelphi export-nb > {} 2>> {}".format(stdoutPath, stderrPath), shell=True)
        self.compareToReferenceYaml(self.stdoutPath(self.version), self.version)


    def test_outputdir(self):
        stderrPath = self.stderrPath(self.version)
        outputDirPath = self.outputDirPath(self.version)
        os.mkdir(outputDirPath)
        subprocess.run("adelphi --output-dir={} export-nb 2>> {}".format(outputDirPath, stderrPath), shell=True)

        outputDirPath = self.outputDirPath(self.version)
        outputSchemas = glob.glob("{}/*/schema".format(outputDirPath))
        self.assertEqual(len(outputSchemas), 1, "Export of nosqlbench config only supports a single keyspace")
        self.compareToReferenceYaml(outputSchemas[0], self.version)
