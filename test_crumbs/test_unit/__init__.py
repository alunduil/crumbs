# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 by Alex Brandt <alunduil@alunduil.com>
#
# crumbs is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import unittest
import tempfile
import os
import sys
import functools
import logging

logger = logging.getLogger(__name__)

try:
    from configparser import SafeConfigParser
except ImportError:
    from ConfigParser import SafeConfigParser

from crumbs import Parameters

class ParametersCreateTest(unittest.TestCase):
    def test_parameters_create(self):
        '''Parameters()

        Check that the default properties of Parameters are set correctly.

        Namespaced parameters are dot separated such as the following:

        * default.param
        * foo.bar

        Properties
        ----------

        :defaults:            dict mapping the namespaced parameter name to the
                              default value for the parameter.
        :parameters:          dict mapping the namespaced parameter name to the
                              parameter tuple for the parameter.
        :configuration_files: dict mapping configuration file paths to
                              configparser for the configuration file.
        :groups:              dict mapping group names to a dict of parameters
                              (like the parameters attribute).
        :parsed:              bool indicating whether full parsing has
                              occurred.

        '''

        p = Parameters()

        self.assertEqual({}, p.defaults)
        self.assertEqual({}, p.parameters)
        self.assertEqual({}, p.configuration_files)
        self.assertEqual(set([ 'default' ]), p.groups)
        self.assertFalse(p.parsed)

class ParametersAddParametersTest(unittest.TestCase):
    def setUp(self):
        self.p = Parameters(conflict_handler = 'resolve')

        self.in_parameters = (
                {
                    'group': 'foo',
                    'options': [ '--bar', '-b' ],
                    'default': 'baz',
                    'type': str,
                    'help': 'assistance is futile',
                    },
                {
                    'group': 'default',
                    'options': [ '--baz', '-b' ],
                    'action': 'store_true',
                    'help': 'assistance is futile',
                    },
                {
                    'options': [ '--qux', '-q' ],
                    'default': 'foo',
                    'help': 'assistance is futile',
                    },
                {
                    'options': [ 'foobar' ],
                    'nargs': '*',
                    'help': 'assistance is futile',
                    },
                {
                    'options': [ '--foobaz' ],
                    'dest': 'quxbaz',
                    },
                {
                    'options': [ '--environment-only' ],
                    'only': [ 'environment' ],
                    },
                )

        self.defaults = {
                'foo.bar': 'baz',
                'default.baz': False,
                'default.qux': 'foo',
                'default.foobar': None,
                'default.quxbaz': None,
                'default.environment_only': None,
                }

        self.parameters = {
                'foo.bar': {
                    'group': 'foo',
                    'options': [ '--bar', '-b' ],
                    'default': 'baz',
                    'type': str,
                    'help': 'assistance is futile',
                    },
                'default.baz': {
                    'group': 'default',
                    'options': [ '--baz', '-b' ],
                    'type': str,
                    'action': 'store_true',
                    'help': 'assistance is futile',
                    },
                'default.qux': {
                    'group': 'default',
                    'options': [ '--qux', '-q' ],
                    'type': str,
                    'default': 'foo',
                    'help': 'assistance is futile',
                    },
                'default.foobar': {
                    'group': 'default',
                    'options': [ 'foobar' ],
                    'type': str,
                    'nargs': '*',
                    'help': 'assistance is futile',
                    },
                'default.quxbaz': {
                    'group': 'default',
                    'options': [ '--foobaz' ],
                    'type': str,
                    'dest': 'quxbaz',
                    },
                'default.environment_only': {
                    'group': 'default',
                    'options': [ '--environment-only' ],
                    'type': str,
                    'only': [ 'environment' ],
                    },
                }

        self.groups = set([
                'default',
                'foo',
                ])

    def test_add_parameters(self):
        '''Parameters().add_parameter()'''

        for parameter in self.in_parameters:
            self.p.add_parameter(**parameter)

        self.assertEqual(self.defaults, self.p.defaults)

        _, self.maxDiff = self.maxDiff, None
        self.assertEqual(self.parameters, self.p.parameters)
        self.maxDiff = _

        self.assertEqual(self.groups, self.p.groups)
        self.assertFalse(self.p.parsed)

class ParametersAddConfigurationFileTest(unittest.TestCase):
    def setUp(self):
        tmp_fh = tempfile.NamedTemporaryFile(mode = 'w')
        tmp_fh.write(
                '[default]\n'
                'foo = bar\n'
                )

        tmp_fh.seek(0)

        self.addCleanup(tmp_fh.close)

        self.file_name = tmp_fh.name

        self.p = Parameters()

    def test_add_configuration_file(self):
        '''Parameters().add_configuration_file()'''

        self.p.add_configuration_file(self.file_name)

        self.assertEqual([ self.file_name ], list(self.p.configuration_files.keys()))
        self.assertIsInstance(self.p.configuration_files[self.file_name], SafeConfigParser)

class ParametersParseParametersTest(unittest.TestCase):
    '''Test the calls without actual parsing.

    This set of tests does not actually test the parsing of the sources but
    only ensures that the state is updated correctly.  Proper parsing and
    retrieval is handled in the read tests below.

    '''

    def setUp(self):
        self.p = Parameters()

    def test_parse(self):
        '''Parameters().parse()'''

        self.p.parse()

        self.assertTrue(self.p.parsed)

    def test_parse_only_known(self):
        '''Parameters().parse(only_known = True)'''

        self.p.parse(only_known = True)

        self.assertFalse(self.p.parsed)

    def test_parse_only_known_with_help(self):
        '''Parameters().parse(only_known = True)—with --help'''

        sys.argv.append('--help')

        self.p.parse(only_known = True)

        sys.argv.remove('--help')

class ParametersReadTest(unittest.TestCase):
    def setUp(self):
        self.original_argv0 = sys.argv[0]

        def _():
            sys.argv[0] = self.original_argv0
        self.addCleanup(_)

        sys.argv[0] = 'crumbs'

        self.p = Parameters()

        self.p.add_parameter(options = ( '--multi', ))

    def populateEnvironment(self):
        os.environ['CRUMBS_ENVIRONMENT_ONLY'] = 'environment_only'
        os.environ['CRUMBS_MULTI'] = 'environment_multi'

        def _(name):
            del os.environ[name]

        self.addCleanup(functools.partial(_, 'CRUMBS_ENVIRONMENT_ONLY'))
        self.addCleanup(functools.partial(_, 'CRUMBS_MULTI'))

        self.p.add_parameter(options = ( '--environment-only', ), only = ( 'environment', ))

    def populateArgumentVector(self):
        sys.argv.extend([ '--argument-only', 'argument_only' ])
        sys.argv.extend([ '--multi', 'argument_multi' ])

        logger.debug('sys.argv: %s', sys.argv)

        self.addCleanup(functools.partial(sys.argv.remove, '--argument-only'))
        self.addCleanup(functools.partial(sys.argv.remove, 'argument_only'))
        self.addCleanup(functools.partial(sys.argv.remove, '--multi'))
        self.addCleanup(functools.partial(sys.argv.remove, 'argument_multi'))

        logger.debug('sys.argv: %s', sys.argv)

        self.p.add_parameter(options = ( '--argument-only', ), only = ( 'argument', ))

    def populateConfiguration(self):
        tmp_fh = tempfile.NamedTemporaryFile(mode = 'w')
        tmp_fh.write(
                '[default]\n'
                'configuration_only = configuration_only\n'
                'multi = configuration_multi\n'
                'type_int = 15\n'
                )

        tmp_fh.seek(0)

        self.addCleanup(tmp_fh.close)

        self.p.add_parameter(options = ( '--configuration-only', ), only = ( 'configuration', ))
        self.p.add_configuration_file(tmp_fh.name)

    def test_read_default_group(self):
        '''Read Parameters—implicit default group

        Verify that the default group is added if no key is found as is.

        '''

        self.populateEnvironment()

        self.p.parse()

        self.assertEqual('environment_only', self.p['environment_only'])
        self.assertEqual('environment_multi', self.p['multi'])

    def test_read_underscores_or_hyphens(self):
        '''Read Parameters—insensitive to '-' vs '_' '''

        self.populateEnvironment()

        self.p.parse()

        self.assertEqual('environment_only', self.p['default.environment-only'])

    def test_read_type(self):
        '''Read Parameters—correct typing'''

        self.populateConfiguration()

        self.p.add_parameter(
                options = [ '--type-int', ],
                type = int,
                default = 10,
                )

        self.p.parse()

        self.assertIsInstance(self.p['default.type_int'], int)
        self.assertEqual(15, self.p['default.type_int'])

    def test_read_environment(self):
        '''Read Parameters—environment'''

        self.populateEnvironment()

        self.p.parse()

        self.assertEqual('environment_only', self.p['default.environment_only'])
        self.assertEqual('environment_multi', self.p['default.multi'])

    def test_read_configuration(self):
        '''Read Parameters—configuration'''

        self.populateConfiguration()

        self.p.parse()

        self.assertEqual('configuration_only', self.p['default.configuration_only'])
        self.assertEqual('configuration_multi', self.p['default.multi'])

    def test_read_argument(self):
        '''Read Parameters—argument'''

        self.populateArgumentVector()

        self.p.parse()

        self.assertEqual('argument_only', self.p['default.argument_only'])
        self.assertEqual('argument_multi', self.p['default.multi'])

    def test_read_environment_configuration(self):
        '''Read Parameters—environment,configuration'''

        self.populateEnvironment()
        self.populateConfiguration()

        self.p.parse()

        self.assertEqual('environment_only', self.p['default.environment_only'])
        self.assertEqual('configuration_only', self.p['default.configuration_only'])
        self.assertEqual('configuration_multi', self.p['default.multi'])

    def test_read_environment_argument(self):
        '''Read Parameters—environment,argument'''

        self.populateEnvironment()
        self.populateArgumentVector()

        self.p.parse()

        self.assertEqual('environment_only', self.p['default.environment_only'])
        self.assertEqual('argument_only', self.p['default.argument_only'])
        self.assertEqual('argument_multi', self.p['default.multi'])

    def test_read_configuration_argument(self):
        '''Read Parameters—configuration,argument'''

        self.populateConfiguration()
        self.populateArgumentVector()

        self.p.parse()

        self.assertEqual('configuration_only', self.p['default.configuration_only'])
        self.assertEqual('argument_only', self.p['default.argument_only'])
        self.assertEqual('argument_multi', self.p['default.multi'])

    def test_read_environment_configuration_argument(self):
        '''Read Parameters—environment,configuration,argument'''

        self.populateEnvironment()
        self.populateConfiguration()
        self.populateArgumentVector()

        self.p.parse()

        self.assertEqual('environment_only', self.p['default.environment_only'])
        self.assertEqual('configuration_only', self.p['default.configuration_only'])
        self.assertEqual('argument_only', self.p['default.argument_only'])
        self.assertEqual('argument_multi', self.p['default.multi'])
