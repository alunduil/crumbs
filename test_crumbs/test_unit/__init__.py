# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 by Alex Brandt <alunduil@alunduil.com>
#
# crumbs is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import argparse
import copy
import functools
import logging
import os
import sys
import tempfile
import time
import unittest

logger = logging.getLogger(__name__)

try:
    from configparser import SafeConfigParser
except ImportError:
    from ConfigParser import SafeConfigParser

from crumbs import Parameters

from test_crumbs.test_fixtures import PARAMETERS_ALL
from test_crumbs.test_fixtures import PARAMETERS_GROUPS
from test_crumbs.test_fixtures import extract_dictionary
from test_crumbs.test_fixtures import group_parameters_dictionary
from test_crumbs.test_fixtures import extract_set

class BaseParametersTest(unittest.TestCase):
    def setUp(self):
        super(BaseParametersTest, self).setUp()

        self.original_parameters = (
                copy.deepcopy(PARAMETERS_ALL),
                copy.deepcopy(PARAMETERS_GROUPS),
                )

        def _():
            global PARAMETERS_ALL, PARAMETERS_GROUPS

            PARAMETERS_ALL, PARAMETERS_GROUPS = self.original_parameters
        self.addCleanup(_)

class ParametersCreateTest(BaseParametersTest):
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
        self.assertEqual({ 'default': {} }, p.grouped_parameters)
        self.assertEqual({}, p.configuration_files)
        self.assertEqual(set([ 'default' ]), p.groups)
        self.assertFalse(p.parsed)

class ParametersAddParametersTest(BaseParametersTest):
    def test_add_parameters(self):
        '''Parameters().add_parameter()'''

        self.p = Parameters()

        self._assert_parameters_added(with_groups = True)

    def test_add_duplicate_parameters(self):
        '''Parameters().add_parameter()—with duplicate'''

        self.p = Parameters()

        self.p.add_parameter(**PARAMETERS_ALL[0]['input'])

        with self.assertRaises(argparse.ArgumentError):
            self.p.add_parameter(**PARAMETERS_ALL[0]['input'])

    def test_add_parameters_no_group_prefix(self):
        '''Parameters(group_prefix = False).add_parameters()'''

        self.p = Parameters(group_prefix = False)

        self._assert_parameters_added()

    def test_add_parameters_resolve_conflict_handler(self):
        '''Parameters(conflict_handler = resolve).add_parameter()'''

        self.p = Parameters(conflict_handler = 'resolve')

        self._assert_parameters_added(with_groups = True)

    def test_add_parameters_no_group_prefix_resolve_conflict_handler(self):
        '''Parameters(group_prefix = False, conflict_handler = resolve).add_parameter()'''

        self.p = Parameters(group_prefix = False, conflict_handler = 'resolve')

        self._assert_parameters_added()

    def _add_groups_to_parameters(self, parameters):
        '''Add the group prefixes to parameters for results checking.'''

        for parameter in parameters.values():
            if parameter['group'] != 'default':
                long_option = max(parameter['options'], key = len)

                parameter['options'].remove(long_option)
                parameter['options'].append(long_option.replace('--', '--' + parameter['group'].replace('_', '-') + '-'))

        return parameters

    def _assert_parameters_added(self, with_groups = False):
        '''Populate and assert values in PARAMETERS_ALL.'''

        for parameter in PARAMETERS_ALL:
            self.p.add_parameter(**parameter['input'])

        self.assertEqual(extract_dictionary(PARAMETERS_ALL, 'default'), self.p.defaults)

        _, self.maxDiff = self.maxDiff, None

        results = extract_dictionary(PARAMETERS_ALL, 'parameter')

        if with_groups:
            results = self._add_groups_to_parameters(results)

        self.assertEqual(results, self.p.parameters)

        results = group_parameters_dictionary(results)

        self.assertEqual(results, self.p.grouped_parameters)

        self.maxDiff = _

        self.assertEqual(extract_set(PARAMETERS_ALL, 'group'), self.p.groups)
        self.assertFalse(self.p.parsed)

class ParametersAddConfigurationFileTest(BaseParametersTest):
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

        self.p.add_parameter(options = ( '--foo', ))

    def test_add_configuration_file(self):
        '''Parameters().add_configuration_file()'''

        self.p.add_configuration_file(self.file_name)

        self.assertEqual([ self.file_name ], list(self.p.configuration_files.keys()))
        self.assertIsInstance(self.p.configuration_files[self.file_name], SafeConfigParser)

    def test_add_configuration_file_with_inotify(self):
        '''Parameters(inotify = True).add_configuration_file()'''

        self.p = Parameters(inotify = True)

        self.p.add_parameter(options = ( '--foo', ))
        self.p.add_parameter(options = ( '--bar', ))

        self.p.add_configuration_file(self.file_name)

        self.p.parse()

        self.assertEqual('bar', self.p['default.foo'])
        self.assertIsNone(self.p['default.bar'])

        with open(self.file_name, 'a') as fh:
            fh.write('bar = foo')

        time.sleep(1)

        self.assertEqual('bar', self.p['default.foo'])
        self.assertEqual('foo', self.p['default.bar'])

class ParametersParseParametersTest(BaseParametersTest):
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

class ParametersGroupingTest(BaseParametersTest):
    def setUp(self):
        super(ParametersGroupingTest, self).setUp()

        self.original_argv0 = sys.argv[0]

        def _():
            sys.argv[0] = self.original_argv0
        self.addCleanup(_)

        sys.argv[0] = 'crumbs'

    def _populate_argument_vector(self, value, argument = lambda _: _['input']['options'][0]):
        for _ in PARAMETERS_GROUPS:
            sys.argv.extend([ argument(_), value ])

            self.addCleanup(functools.partial(sys.argv.remove, argument(_)))
            self.addCleanup(functools.partial(sys.argv.remove, value))

            self.p.add_parameter(**_['input'])

    def _assert_parameters(self, value):
        for _ in PARAMETERS_GROUPS:
            logger.debug('_: %s', _)
            self.assertEqual(value, self.p[list(_['parameter'])[0]])

    def test_parameters_with_groups(self):
        self.p = Parameters(group_prefix = True)

        self._populate_argument_vector('with_group',
                lambda _: _['input']['options'][0].replace('--', '--' + _['input']['group'].replace('_', '-') + '-')
                )

        self.p.parse()

        self._assert_parameters('with_group')

    def test_parameters_without_groups(self):
        self.p = Parameters(group_prefix = False)

        self._populate_argument_vector('without_group')

        self.p.parse()

        self._assert_parameters('without_group')

class ParametersReadTest(BaseParametersTest):
    def setUp(self):
        super(ParametersReadTest, self).setUp()

        self.original_argv0 = sys.argv[0]

        def _():
            sys.argv[0] = self.original_argv0
        self.addCleanup(_)

        sys.argv[0] = 'crumbs'

        self.p = Parameters()

        self.p.add_parameter(options = [ '--multi', ])

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

        self.p.add_parameter(options = [ '--argument-only', ], only = ( 'argument', ))

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
