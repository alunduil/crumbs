# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 by Alex Brandt <alunduil@alunduil.com>
#
# parameters is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import unittest
import tempfile
import os
import sys
import functools

from parameters import Parameters

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
                )

        self.defaults = {
                'foo.bar': 'baz',
                'default.baz': False,
                'default.qux': 'foo',
                'default.foobar': None,
                'default.quxbaz': None,
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
                    'action': 'store_true',
                    'help': 'assistance is futile',
                    },
                'default.qux': {
                    'group': 'default',
                    'options': [ '--qux', '-q' ],
                    'default': 'foo',
                    'help': 'assistance is futile',
                    },
                'default.foobar': {
                    'group': 'default',
                    'options': [ 'foobar' ],
                    'nargs': '*',
                    'help': 'assistance is futile',
                    },
                'default.quxbaz': {
                    'group': 'default',
                    'options': [ '--foobaz' ],
                    'dest': 'quxbaz',
                    },
                }

        self.groups = set([
                'default',
                'foo',
                ])

    def test_add_parameters(self):
        for parameter in self.in_parameters:
            self.p.add_parameter(**parameter)

        self.assertEqual(self.defaults, self.p.defaults)

        _ = self.maxDiff
        self.maxDiff = None
        self.assertEqual(self.parameters, self.p.parameters)
        self.maxDiff = _

        self.assertEqual(self.groups, self.p.groups)
        self.assertFalse(self.p.parsed)

class ParametersAddConfigurationFileTest(unittest.TestCase):
    pass

class ParametersParseParametersTest(unittest.TestCase):
    pass

class ParametersReadTest(unittest.TestCase):
    def setUp(self):
        self.original_argv0 = sys.argv[0]

        def _():
            sys.argv[0] = self.original_argv0
        self.addCleanup(_)

        sys.argv[0] = 'parameters'

        self.p = Parameters()

    def populateEnvironment(self):
        os.environ['PARAMETERS_ENV_ONLY'] = 'environment_only'
        os.environ['PARAMETERS_MULTI'] = 'environment_multi'

        def _(name):
            del os.environ[name]

        self.addCleanup(functools.partial(_, 'PARAMETERS_ENV_ONLY'))
        self.addCleanup(functools.partial(_, 'PARAMETERS_MULTI'))

    def populateArgumentVector(self):
        sys.argv.extend([ '--argument-only', 'argument_only' ])
        sys.argv.extend([ '--multi', 'argument_multi' ])

        def _(name):
            sys.argv.remove(name)

        self.addCleanup(functools.partial(_, '--argument-only'))
        self.addCleanup(functools.partial(_, 'argument_only'))
        self.addCleanup(functools.partial(_, '--multi'))
        self.addCleanup(functools.partial(_, 'argument_only'))

    def populateConfiguration(self):
        tmp_fh = tempfile.NamedTemporaryFile()
        tmp_fh.write(
                '[default]\n'
                'configuration_only = configuration_only\n'
                'multi = configuration_multi\n'
                )

        tmp_fh.seek(0)

        self.addCleanup(tmp_fh.close)

    def test_read_environment(self):
        '''Parameters—environment'''

        self.populateEnvironment()

    def test_read_environment_only(self):
        pass

    def test_read_configuration_only(self):
        pass

    def test_read_argument_only(self):
        pass

    def test_read_environment_multi(self):
        pass

    def test_read_configuration_multi(self):
        pass

    def test_read_argument_multi(self):
        pass
