# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 by Alex Brandt <alunduil@alunduil.com>
#
# crumbs is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import argparse
import copy
import functools
import logging
import sys

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from crumbs import Parameters
from crumbs import _pyinotify_loaded

from test_crumbs.test_common import BaseParametersTest

logger = logging.getLogger(__name__)


class ParametersCreateTest(unittest.TestCase):
    def _assert_properties_set(self):
        self.assertEqual({}, self.p.defaults)
        self.assertEqual({}, self.p.parameters)
        self.assertEqual({ 'default': {} }, self.p.grouped_parameters)
        self.assertEqual({}, self.p.configuration_files)
        self.assertEqual(set([ 'default' ]), self.p.groups)
        self.assertFalse(self.p.parsed)

    def test_parameters_create_no_paramters(self):
        '''Parameters()'''

        self.p = Parameters()

        self._assert_properties_set()

    @unittest.skipUnless(_pyinotify_loaded, 'inotify module not available')
    def test_parameters_create_inotify_true(self):
        '''Parameters(inotify = True)'''

        self.p = Parameters(inotify = True)

        self._assert_properties_set()


class ParametersAddParametersTest(BaseParametersTest):
    def _assert_parameters_add(self, parameters, group_prefix = True):
        for inputs in parameters['inputs']:
            self.p.add_parameter(**inputs)

        logger.debug('defaults: %s', self.p.defaults)
        self.assertEqual(parameters['defaults'], self.p.defaults)

        if group_prefix:
            logger.info('adding group prefixes to arguments')

            def _add_group_to_long_options(parameters):
                for _ in parameters:
                    if _['group'] != 'default':
                        long_option = max(_['options'], key = len)

                        _['options'].remove(long_option)
                        _['options'].append(long_option.replace('--', '--' + _['group'].replace('_', '-') + '-'))

            _add_group_to_long_options(parameters['parameters'].values())

            for _ in parameters['grouped_parameters'].values():
                _add_group_to_long_options(_.values())

        logger.debug('parameters.keys(): %s', parameters.keys())

        _, self.maxDiff = self.maxDiff, None

        logger.debug('parameters: %s', self.p.parameters)
        self.assertEqual(parameters['parameters'], self.p.parameters)

        logger.debug('grouped_parameters: %s', self.p.grouped_parameters)
        self.assertEqual(parameters['grouped_parameters'], self.p.grouped_parameters)

        self.maxDiff = _

        logger.debug('groups: %s', self.p.groups)
        self.assertEqual(parameters['groups'], self.p.groups)

        self.assertFalse(self.p.parsed)

    def test_add_parameters_with_group_prefix(self):
        '''Parameters().add_parameter()'''

        self.p = Parameters()

        self._assert_parameters_add(self.parameters['valid'])

    def test_add_parameters_without_group_prefix(self):
        '''Parameters(group_prefix = False).add_parameters()'''

        self.p = Parameters(group_prefix = False)

        self._assert_parameters_add(self.parameters['valid'], group_prefix = False)

    def test_add_parameters_with_group_prefix_resolve_conflict_handler(self):
        '''Parameters(conflict_handler = resolve).add_parameter()'''

        self.p = Parameters(conflict_handler = 'resolve')

        self._assert_parameters_add(self.parameters['valid'])

    def test_add_parameters_without_group_prefix_resolve_conflict_handler(self):
        '''Parameters(group_prefix = False, conflict_handler = resolve).add_parameter()'''

        self.p = Parameters(group_prefix = False, conflict_handler = 'resolve')

        self._assert_parameters_add(self.parameters['valid'], group_prefix = False)

    def test_add_duplicate_parameters(self):
        '''Parameters().add_parameter()—with duplicate'''

        self.p = Parameters()

        self.p.add_parameter(**copy.deepcopy(self.parameters['valid']['inputs'][0]))

        with self.assertRaises(argparse.ArgumentError):
            self.p.add_parameter(**copy.deepcopy(self.parameters['valid']['inputs'][0]))

    def test_add_duplicate_parameters_resolve_conflict_handler(self):
        '''Parameters(conflict_handler = resolve).add_parameter()—with duplicate'''

        self.p = Parameters(conflict_handler = 'resolve')

        self.p.add_parameter(**copy.deepcopy(self.parameters['valid']['inputs'][0]))
        self.p.add_parameter(**copy.deepcopy(self.parameters['valid']['inputs'][0]))


class ParametersParseTest(unittest.TestCase):
    def setUp(self):
        self.p = Parameters()

    def test_parse(self):
        '''Parameters().parse()'''

        self.p.parse()

        self.assertTrue(self.p.parsed)

    def test_parse_with_help(self):
        '''Parameters().parse()—with --help'''

        sys.argv.append('--help')
        self.addCleanup(functools.partial(sys.argv.remove, '--help'))

        with self.assertRaises(SystemExit):
            self.p.parse()

    def test_parse_only_known(self):
        '''Parameters().parse(only_known = True)'''

        self.p.parse(only_known = True)

        self.assertFalse(self.p.parsed)

    def test_parse_only_known_with_help(self):
        '''Parameters().parse(only_known = True)—with --help'''

        sys.argv.append('--help')
        self.addCleanup(functools.partial(sys.argv.remove, '--help'))

        self.p.parse(only_known = True)

        self.assertFalse(self.p.parsed)
