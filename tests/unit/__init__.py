import os
import random
import shutil
import string
import tempfile
from unittest import TestCase

def random_directory():
    dirname = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    directory = tempfile.mkdtemp(suffix=dirname)
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

class FileTestCase(TestCase):
    def setUp(self):
        super(FileTestCase, self).setUp()
        self.args = {}
        dirname = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        filename = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        # This will create a psuedo-random temporary directory on the machine
        # which runs the unit tests, but NOT on the machine where elasticsearch
        # is running. This means tests may fail if run against remote instances
        # unless you explicitly set `self.args['location']` to a proper spot
        # on the target machine.
        self.written_value = '''NOTHING'''
        self.args['tmpdir'] = tempfile.mkdtemp(suffix=dirname)
        if not os.path.exists(self.args['tmpdir']):
            os.makedirs(self.args['tmpdir'])
        self.args['configdir'] = random_directory()
        self.args['configfile'] = os.path.join(self.args['configdir'], 'es_client.yml')
        self.args['filename'] = os.path.join(self.args['tmpdir'], filename)
        self.args['no_file_here'] = os.path.join(self.args['tmpdir'], 'not_created')
        with open(self.args['filename'], 'w') as f:
            f.write(self.written_value)

    def tearDown(self):
        if os.path.exists(self.args['tmpdir']):
            shutil.rmtree(self.args['tmpdir'])

    def write_config(self, fname, data):
        with open(fname, 'w') as f:
            f.write(data)