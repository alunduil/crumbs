# Copyright (C) 2013 by Alex Brandt <alunduil@alunduil.com>
#
# parameters is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import unittest
import mock

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
        self.assertEqual([ 'default' ], p.groups)
        self.assertFalse(p.parsed)

class ParametersReadTest(unittest.TestCase):
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

class ParametersUpdateTest(unittest.TestCase):
    pass

class ParametersDeleteTest(unittest.TestCase):
    pass

class ParametersAddParametersTest(unittest.TestCase):
    pass

class ParametersAddConfigurationFileTest(unittest.TestCase):
    pass

class ParametersParseParametersTest(unittest.TestCase):
    pass
