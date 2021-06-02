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

class TestNbExportStdoutTemplateVars(unittest.TestCase, SchemaTestMixin, ExportNbMixin):

    def setUp(self):
        super(TestNbExportStdoutTemplateVars, self).setUp()


    def getBaseSchemaPath(self):
        return self.nbBaseSchema()


    def runAdelphi(self, version=None):
        stdoutPath = self.stdoutPath(version)
        stderrPath = self.stderrPath(version)
        cmdStr = "adelphi export-nb > {} 2>> {}"
        subprocess.run(cmdStr.format(stdoutPath, stderrPath), shell=True)


    def evalAdelphiOutput(self, version=None):
        self.maxDiff = None
        self.compareToReferenceYaml(self.nbReferenceYaml("{}-templatevars".format(version)), self.stdoutPath(version))