# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 by Alex Brandt <alunduil@alunduil.com>
#
# crumbs is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import copy
import logging

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from test_crumbs.test_fixtures import PARAMETERS

logger = logging.getLogger(__name__)


class BaseParametersTest(unittest.TestCase):
    def setUp(self):
        super(BaseParametersTest, self).setUp()

        self.parameters = copy.deepcopy(PARAMETERS)
