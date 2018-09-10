# -*- coding: utf-8 -*-

"""Common test utilities for crumbs."""

import copy
import logging
import unittest

from crumbs_test.fixtures_test import PARAMETERS

LOGGER = logging.getLogger(__name__)


class BaseParametersTest(unittest.TestCase):
    """Base Parameter Test Class."""

    def setUp(self) -> None:
        super(BaseParametersTest, self).setUp()

        self.parameters = copy.deepcopy(PARAMETERS)
