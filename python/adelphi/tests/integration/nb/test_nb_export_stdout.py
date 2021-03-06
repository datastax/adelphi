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

class TestNbExportStdout(unittest.TestCase, SchemaTestMixin, ExportNbMixin):

    def setUp(self):
        super(TestNbExportStdout, self).setUp()


    def getBaseSchemaPath(self):
        return "tests/integration/resources/nb-base-schema.cql"


    def runAdelphi(self, version=None):
        stdoutPath = self.stdoutPath(version)
        stderrPath = self.stderrPath(version)
        subprocess.run("adelphi export-nb > {} 2>> {}".format(stdoutPath, stderrPath), shell=True)


    def evalAdelphiOutput(self, version=None):
        self.compareToReferenceYaml(self.stdoutPath(version), version)
