# -*- coding: utf-8 -*-

"""Common test utilities for crumbs."""

import copy
import logging
import sys
import unittest

from crumbs_test.fixtures_test import PARAMETERS

LOGGER = logging.getLogger(__name__)


class BaseParametersTest(unittest.TestCase):
    """Base Parameter Test Class."""

    def setUp(self) -> None:
        super(BaseParametersTest, self).setUp()

        self.parameters = copy.deepcopy(PARAMETERS)

        self.original_argv = sys.argv

        def _() -> None:
            sys.argv = self.original_argv

        self.addCleanup(_)

        sys.argv = ["crumbs"]
