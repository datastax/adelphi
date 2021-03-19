import glob
import logging
import os
import shutil
import sys
import yaml

try:
    import unittest2 as unittest
except ImportError:
    import unittest

if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as subprocess
else:
    import subprocess

from tests.integration import SchemaTestMixin

log = logging.getLogger('adelphi')

class TestNb(unittest.TestCase, SchemaTestMixin):

    def setUp(self):
        super(TestNb, self).setUp()


    def getBaseSchemaPath(self):
        return "tests/integration/resources/nb-base-schema.cql"


    def runAdelphi(self, version=None):
        exportCmd = "export-nb"
        stdoutPath = self.stdoutPath(version)
        stderrPath = self.stderrPath(version)
        subprocess.run("adelphi {} > {} 2>> {}".format(exportCmd, stdoutPath, stderrPath), shell=True)
        outputDirPath = self.outputDirPath(version)
        os.mkdir(outputDirPath)
        subprocess.run("adelphi --output-dir={} {} 2>> {}".format(outputDirPath, exportCmd, stderrPath), shell=True)


    def _compareToReference(self, comparePath, version=None):
        referencePath = "tests/integration/resources/nb-schemas/{}.yaml".format(version)
        # Loader specification here to avoid a deprecation warning... see https://msg.pyyaml.org/load
        referenceYaml = yaml.load(open(referencePath), Loader=yaml.FullLoader)
        compareYaml = yaml.load(open(comparePath), Loader=yaml.FullLoader)
        self.assertEqual(referenceYaml, compareYaml)


    def evalAdelphiOutput(self, version=None):

        # Compare process for stdout
        self._compareToReference(self.stdoutPath(version), version)

        # Compare process for output dir
        outputDirPath = self.outputDirPath(version)
        outputSchemas = glob.glob("{}/*/schema".format(outputDirPath))
        self.assertEqual(len(outputSchemas), 1, "Export of nosqlbench config only supports a single keyspace")
        self._compareToReference(outputSchemas[0], version)
