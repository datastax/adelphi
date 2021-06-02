import glob
import logging
import os
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
from tests.integration.nb import ExportNbMixin

log = logging.getLogger('adelphi')

class TestNbExportOutputDirTemplateVars(unittest.TestCase, SchemaTestMixin, ExportNbMixin):

    def setUp(self):
        super(TestNbExportOutputDirTemplateVars, self).setUp()


    def getBaseSchemaPath(self):
        return self.nbBaseSchema()


    def runAdelphi(self, version=None):
        stderrPath = self.stderrPath(version)
        outputDirPath = self.outputDirPath(version)
        os.mkdir(outputDirPath)
        cmdStr = "adelphi --output-dir={} export-nb 2>> {}"
        subprocess.run(cmdStr.format(outputDirPath, stderrPath), shell=True)


    def evalAdelphiOutput(self, version=None):
        outputDirPath = self.outputDirPath(version)
        outputSchemas = glob.glob("{}/*/schema".format(outputDirPath))
        self.assertEqual(len(outputSchemas), 1, "Export of nosqlbench config only supports a single keyspace")
        self.compareToReferenceYaml(self.nbReferenceYaml("{}-templatevars".format(version)), outputSchemas[0])