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
from tests.integration.cql import ExportCqlMixin

log = logging.getLogger('adelphi')

class TestCqlExportStdout(unittest.TestCase, SchemaTestMixin, ExportCqlMixin):

    def setUp(self):
        super(TestCqlExportStdout, self).setUp()


    def runAdelphi(self, version):
        stdoutPath = self.stdoutPath(version)
        stderrPath = self.stderrPath(version)
        subprocess.run("adelphi export-cql --no-metadata > {} 2>> {}".format(stdoutPath, stderrPath), shell=True)


    def evalAdelphiOutput(self, version):
        referencePath = "tests/integration/resources/cql-schemas/{}.cql".format(version)
        self.compareToReferenceCql(referencePath, self.stdoutPath(version))


