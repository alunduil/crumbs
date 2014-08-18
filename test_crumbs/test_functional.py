# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 by Alex Brandt <alunduil@alunduil.com>
#
# crumbs is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import functools
import os
import sys
import tempfile
import time

try:
    import unittest2 as unittest
except ImportError:
    import unittest

try:
    from configparser import SafeConfigParser
except ImportError:
    from ConfigParser import SafeConfigParser

from crumbs import Parameters
from crumbs import _pyinotify_loaded

from test_crumbs.test_common import BaseParametersTest


class ParametersAddConfigurationFileTest(BaseParametersTest):
    def setUp(self):
        super(ParametersAddConfigurationFileTest, self).setUp()

        tmp_fh = tempfile.NamedTemporaryFile(mode = 'w')
        tmp_fh.write(
            '[default]\n'
            'foo = bar\n'
        )

        tmp_fh.seek(0)

        self.addCleanup(tmp_fh.close)

        self.file_name = tmp_fh.name

    def _assert_configuration_readable(self):
        self.p.add_parameter(options = ( '--foo', ))
        self.p.add_parameter(options = ( '--bar', ))

        self.p.add_configuration_file(self.file_name)

        self.assertEqual([ self.file_name ], list(self.p.configuration_files.keys()))
        self.assertIsInstance(self.p.configuration_files[self.file_name], SafeConfigParser)

        self.p.parse()

        self.assertEqual('bar', self.p['default.foo'])
        self.assertIsNone(self.p['default.bar'])

    def test_add_configuration_file(self):
        '''Parameters().add_configuration_file()'''

        self.p = Parameters()

        self._assert_configuration_readable()

    @unittest.skipUnless(_pyinotify_loaded, 'inotify module not available')
    def test_add_configuration_file_with_inotify(self):
        '''Parameters(inotify = True).add_configuration_file()'''

        self.p = Parameters(inotify = True)

        self._assert_configuration_readable()

        with open(self.file_name, 'a') as fh:
            fh.write('bar = foo')

        time.sleep(1)

        self.assertEqual('bar', self.p['default.foo'])
        self.assertEqual('foo', self.p['default.bar'])


class ParametersReadTest(unittest.TestCase):
    def setUp(self):
        self.original_argv0 = sys.argv[0]

        def _():
            sys.argv[0] = self.original_argv0
        self.addCleanup(_)

        sys.argv[0] = 'crumbs'

        self.p = Parameters()

    def populateMulti(self, group = False):
        self.p.add_parameter(options = [ '--multi', ])

    def populateEnvironment(self):
        os.environ['CRUMBS_ENVIRONMENT_ONLY'] = 'environment_only'
        os.environ['CRUMBS_MULTI'] = 'environment_multi'

        self.addCleanup(functools.partial(os.unsetenv, 'CRUMBS_ENVIRONMENT_ONLY'))
        self.addCleanup(functools.partial(os.unsetenv, 'CRUMBS_MULTI'))

        self.p.add_parameter(options = ( '--environment-only', ), only = ( 'environment', ))

    def populateArgumentVector(self):
        sys.argv.extend([ '--argument-only', 'argument_only' ])
        sys.argv.extend([ '--multi', 'argument_multi' ])

        self.addCleanup(functools.partial(sys.argv.remove, '--argument-only'))
        self.addCleanup(functools.partial(sys.argv.remove, 'argument_only'))
        self.addCleanup(functools.partial(sys.argv.remove, '--multi'))
        self.addCleanup(functools.partial(sys.argv.remove, 'argument_multi'))

        self.p.add_parameter(options = [ '--argument-only', ], only = ( 'argument', ))

    def populateConfiguration(self):
        tmp_fh = tempfile.NamedTemporaryFile(mode = 'w')
        tmp_fh.write(
            '[default]\n'
            'configuration_only = configuration_only\n'
            'multi = configuration_multi\n'
            '\n'
            'type_int = 15\n'
        )

        tmp_fh.seek(0)

        self.addCleanup(tmp_fh.close)

        self.p.add_parameter(options = ( '--configuration-only', ), only = ( 'configuration', ))
        self.p.add_configuration_file(tmp_fh.name)

    def populateTypes(self):
        sys.argv.extend([ '--type-int', '15' ])

        self.addCleanup(functools.partial(sys.argv.remove, '--type-int'))
        self.addCleanup(functools.partial(sys.argv.remove, '15'))

        self.p.add_parameter(options = [ '--type-int', ], type = int, default = 0)

    def test_read_implicit_default_group(self):
        '''Parameters()[key]—implicit default group'''

        self.populateEnvironment()

        self.p.parse()

        self.assertEqual('environment_only', self.p['environment_only'])
        self.assertEqual('environment_only', self.p['default.environment_only'])

    def test_read_underscores_or_hyphens(self):
        '''Parameters()[key]—indistinguishable characters: -, _'''

        self.populateEnvironment()

        self.p.parse()

        self.assertEqual('environment_only', self.p['environment-only'])
        self.assertEqual('environment_only', self.p['environment_only'])

    def test_read_types(self):
        '''Parameters()[key]—type cast'''

        self.populateTypes()

        self.p.parse()

        self.assertIsInstance(self.p['type_int'], int)
        self.assertEqual(15, self.p['type_int'])

    def test_read_custom_environment_prefix(self):
        '''Parameters()[key]—environment_prefix=custom'''

        os.environ['CUSTOM_CUSTOM_ENVIRONMENT'] = 'custom_environment'

        self.addCleanup(functools.partial(os.unsetenv, 'CUSTOM_CUSTOM_ENVIRONMENT'))

        self.p.add_parameter(options = ( '--custom-environment', ), only = ( 'environment', ), environment_prefix = 'custom')

        self.p.parse()

        self.assertEqual('custom_environment', self.p['custom_environment'])

    def test_read_empty_environment_prefix(self):
        '''Parameters()[key]—environment_prefix=None'''

        os.environ['CUSTOM_ENVIRONMENT'] = 'custom_environment'

        self.addCleanup(functools.partial(os.unsetenv, 'CUSTOM_ENVIRONMENT'))

        self.p.add_parameter(options = ( '--custom-environment', ), only = ( 'environment', ), environment_prefix = None)

        self.p.parse()

        self.assertEqual('custom_environment', self.p['custom_environment'])

    def test_read_environment_with_expansion(self):
        '''Parameters()[key]—with expansion'''

        os.environ['FOO'] = 'foo'
        self.addCleanup(functools.partial(os.unsetenv, 'FOO'))

        os.environ['EXPAND'] = '${FOO}'
        self.addCleanup(functools.partial(os.unsetenv, 'EXPAND'))

        self.p.add_parameter(options = ( '--expand', ), only = ( 'environment', ), environment_prefix = None)

        self.p.parse()

        self.assertEqual('foo', self.p['expand'])

    def test_read_environment(self):
        '''Parameters()[key]—environment'''

        self.populateEnvironment()
        self.populateMulti()

        self.p.parse()

        self.assertEqual('environment_only', self.p['environment_only'])
        self.assertEqual('environment_multi', self.p['multi'])

    def test_read_configuration(self):
        '''Parameters()[key]—configuration'''

        self.populateConfiguration()
        self.populateMulti()

        self.p.parse()

        self.assertEqual('configuration_only', self.p['configuration_only'])
        self.assertEqual('configuration_multi', self.p['multi'])

    def test_read_argument(self):
        '''Parameters()[key]—argument'''

        self.populateArgumentVector()
        self.populateMulti()

        self.p.parse()

        self.assertEqual('argument_only', self.p['argument_only'])
        self.assertEqual('argument_multi', self.p['multi'])

    def test_read_environment_configuration(self):
        '''Parameters()[key]—environment,configuration'''

        self.populateEnvironment()
        self.populateConfiguration()
        self.populateMulti()

        self.p.parse()

        self.assertEqual('environment_only', self.p['environment_only'])
        self.assertEqual('configuration_only', self.p['configuration_only'])
        self.assertEqual('configuration_multi', self.p['multi'])

    def test_read_environment_argument(self):
        '''Parameters()[key]—environment,argument'''

        self.populateEnvironment()
        self.populateArgumentVector()
        self.populateMulti()

        self.p.parse()

        self.assertEqual('environment_only', self.p['environment_only'])
        self.assertEqual('argument_only', self.p['argument_only'])
        self.assertEqual('argument_multi', self.p['multi'])

    def test_read_configuration_argument(self):
        '''Parameters()[key]—configuration,argument'''

        self.populateConfiguration()
        self.populateArgumentVector()
        self.populateMulti()

        self.p.parse()

        self.assertEqual('configuration_only', self.p['configuration_only'])
        self.assertEqual('argument_only', self.p['argument_only'])
        self.assertEqual('argument_multi', self.p['multi'])

    def test_read_environment_configuration_argument(self):
        '''Parameters()[key]—environment,configuration,argument'''

        self.populateEnvironment()
        self.populateConfiguration()
        self.populateArgumentVector()
        self.populateMulti()

        self.p.parse()

        self.assertEqual('environment_only', self.p['environment_only'])
        self.assertEqual('configuration_only', self.p['configuration_only'])
        self.assertEqual('argument_only', self.p['argument_only'])
        self.assertEqual('argument_multi', self.p['multi'])
