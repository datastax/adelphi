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
from tests.integration.cql import ExportCqlMixin

log = logging.getLogger('adelphi')

# Implemented for https://github.com/datastax/adelphi/issues/106.
#
# We should see exactly one keyspace schema written to the output dir and that file
# should match up exactly to the requested keyspace
class TestCqlExportOutputDirSomeKeyspaces(unittest.TestCase, SchemaTestMixin, ExportCqlMixin):

    def setUp(self):
        super(TestCqlExportOutputDirSomeKeyspaces, self).setUp()


    def runAdelphi(self, version):
        stderrPath = self.stderrPath(version)
        outputDirPath = self.outputDirPath(version)
        os.mkdir(outputDirPath)
        subprocess.run("adelphi --output-dir={} --keyspaces=my_ks_0 export-cql --no-metadata 2>> {}".format(outputDirPath, stderrPath), shell=True)


    def evalAdelphiOutput(self, version):
        referencePath = "tests/integration/resources/cql-schemas/{}-ks0.cql".format(version)
        outputDirPath = self.outputDirPath(version)
        outputSchemas = glob.glob("{}/*/schema".format(outputDirPath))
        self.assertEqual(len(outputSchemas), 1)
        self.compareToReferenceCql(referencePath, outputSchemas[0])
