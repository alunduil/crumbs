# -*- coding: utf-8 -*-

"""Unit Tests for Crumbs."""

import argparse
import copy
import functools
import logging
import sys
import unittest
from typing import Any, Dict

from crumbs import Parameters
from crumbs_test.common_test import BaseParametersTest

LOGGER = logging.getLogger(__name__)


class ParametersCreateTest(unittest.TestCase):
    """Create Paramters Tests."""

    def _assert_properties_set(self) -> None:
        self.assertEqual({}, self.p.defaults)
        self.assertEqual({}, self.p.parameters)
        self.assertEqual({"default": {}}, self.p.grouped_parameters)
        self.assertEqual({}, self.p.configuration_files)
        self.assertEqual(set(["default"]), self.p.groups)
        self.assertFalse(self.p.parsed)

    def test_parameters_create_no_paramters(self) -> None:
        """Parameters()"""

        self.p = Parameters()  # pylint: disable=attribute-defined-outside-init,invalid-name

        self._assert_properties_set()


class ParametersAddParametersTest(BaseParametersTest):
    """Add Parameters Tests."""

    def _assert_parameters_add(self, parameters: Dict[str, Any], group_prefix: bool = True) -> None:
        for inputs in parameters["inputs"]:
            self.p.add_parameter(**inputs)

        LOGGER.debug("defaults: %s", self.p.defaults)
        self.assertEqual(parameters["defaults"], self.p.defaults)

        if group_prefix:
            LOGGER.info("adding group prefixes to arguments")

            def _add_group_to_long_options(parameters: Dict[str, Any]) -> None:
                for _ in parameters:
                    if _["group"] != "default":
                        long_option = max(_["options"], key=len)

                        _["options"].remove(long_option)
                        _["options"].append(long_option.replace("--", "--" + _["group"].replace("_", "-") + "-"))

            _add_group_to_long_options(parameters["parameters"].values())

            for _ in parameters["grouped_parameters"].values():
                _add_group_to_long_options(_.values())

        LOGGER.debug("parameters.keys(): %s", parameters.keys())

        _, self.maxDiff = self.maxDiff, None  # pylint: disable=attribute-defined-outside-init,invalid-name

        LOGGER.debug("parameters: %s", self.p.parameters)
        self.assertEqual(parameters["parameters"], self.p.parameters)

        LOGGER.debug("grouped_parameters: %s", self.p.grouped_parameters)
        self.assertEqual(parameters["grouped_parameters"], self.p.grouped_parameters)

        self.maxDiff = _  # pylint: disable=attribute-defined-outside-init

        LOGGER.debug("groups: %s", self.p.groups)
        self.assertEqual(parameters["groups"], self.p.groups)

        self.assertFalse(self.p.parsed)

    def test_add_parameters_with_group_prefix(self) -> None:
        """Parameters().add_parameter()"""

        self.p = Parameters()  # pylint: disable=attribute-defined-outside-init,invalid-name

        self._assert_parameters_add(self.parameters["valid"])

    def test_add_parameters_without_group_prefix(self) -> None:
        """Parameters(group_prefix = False).add_parameters()"""

        self.p = Parameters(group_prefix=False)  # pylint: disable=attribute-defined-outside-init

        self._assert_parameters_add(self.parameters["valid"], group_prefix=False)

    def test_add_parameters_with_group_prefix_resolve_conflict_handler(self) -> None:
        """Parameters(conflict_handler = resolve).add_parameter()"""

        self.p = Parameters(conflict_handler="resolve")  # pylint: disable=attribute-defined-outside-init

        self._assert_parameters_add(self.parameters["valid"])

    def test_add_parameters_without_group_prefix_resolve_conflict_handler(self) -> None:
        """Parameters(group_prefix = False, conflict_handler = resolve).add_parameter()"""

        self.p = Parameters(  # pylint: disable=attribute-defined-outside-init
            group_prefix=False, conflict_handler="resolve"
        )  # pylint: disable=attribute-defined-outside-init

        self._assert_parameters_add(self.parameters["valid"], group_prefix=False)

    def test_add_duplicate_parameters(self) -> None:
        """Parameters().add_parameter()—with duplicate"""

        self.p = Parameters()  # pylint: disable=attribute-defined-outside-init

        self.p.add_parameter(**copy.deepcopy(self.parameters["valid"]["inputs"][0]))

        with self.assertRaises(argparse.ArgumentError):
            self.p.add_parameter(**copy.deepcopy(self.parameters["valid"]["inputs"][0]))

    def test_add_duplicate_parameters_resolve_conflict_handler(self) -> None:
        """Parameters(conflict_handler = resolve).add_parameter()—with duplicate"""

        self.p = Parameters(conflict_handler="resolve")  # pylint: disable=attribute-defined-outside-init

        self.p.add_parameter(**copy.deepcopy(self.parameters["valid"]["inputs"][0]))
        self.p.add_parameter(**copy.deepcopy(self.parameters["valid"]["inputs"][0]))


class ParametersParseTest(unittest.TestCase):
    """Parse Parameters Tests."""

    def setUp(self) -> None:
        self.p = Parameters()  # pylint: disable=invalid-name

    def test_parse(self) -> None:
        """Parameters().parse()"""

        self.p.parse()

        self.assertTrue(self.p.parsed)

    def test_parse_with_help(self) -> None:
        """Parameters().parse()—with --help"""

        sys.argv.append("--help")
        self.addCleanup(functools.partial(sys.argv.remove, "--help"))

        try:
            self.p.parse()
        except SystemExit:
            pass

        self.fail("expected SystemExit to be raised")

        # The following doesn't type due to SystemExit deriving from
        # BaseException rather than Exception.
        # with self.assertRaises(SystemExit):
        #    self.p.parse()

    def test_parse_only_known(self) -> None:
        """Parameters().parse(only_known = True)"""

        self.p.parse(only_known=True)

        self.assertFalse(self.p.parsed)

    def test_parse_only_known_with_help(self) -> None:
        """Parameters().parse(only_known = True)—with --help"""

        sys.argv.append("--help")
        self.addCleanup(functools.partial(sys.argv.remove, "--help"))

        self.p.parse(only_known=True)

        self.assertFalse(self.p.parsed)
