# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 by Alex Brandt <alunduil@alunduil.com>
#
# crumbs is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

"""Provides an easy to use multi-source parameter container.

:``Parameters``:        Queryable collection of parameters whose values are set
                        by the user.
:``information``:       Miscellaneous information about crumbs (i.e. version).

"""

import argparse
import copy
import inspect
import functools
import logging
import os
import re
import sys
import warnings

from configparser import SafeConfigParser
from configparser import NoOptionError
from configparser import NoSectionError
from typing import Any, Dict, Optional, List, Sequence, Callable, Union

LOGGER = logging.getLogger(__name__)
LOGGER.propagate = False
LOGGER.addHandler(logging.NullHandler())


class Parameters:  # pylint: disable=too-many-instance-attributes
    """Queryable collection of parameters whose values are set by the user.

    Using the normal dictionary lookup mechanism (D[]), one can obtain the user
    set values for particular parameters (set in command line arguments,
    configuration files, or environment variables) which have been added to
    ``Parameters``.

    The three sources (command line arguments, configuration files, and
    environment variables) can have values for parameters.  When two or more
    sources define values for the same parameter, the first source (highest
    precedence) in the following list will provide the value for that parameter:

    :command line arguments: Values parsed from ``sys.argv``.
    :configuration files:    Values set in registered ``ini`` files.
    :environment variables:  Values set in environment variables.
    :defaults:               Default value (if set for the parameter).

    Parameters are added via the ``add_parameter`` method.  Configuration files
    that should be searched can be added with the ``add_configuration_file``
    method.  Environment variables are prefixed with an uppercase program name
    (``sys.argv[0]``) and uppercased with dots '.' and hyphens '-' replaced with
    underscores (i.e. ARGV0_GROUP_LONG_OPTION where group may be ommitted if it
    is 'default').

    Before querying for parameters' values, the ``Parameters`` object must have
    been parsed with the ``parse`` method.  Parsing ensures that the command
    line, configuration files, and environment variables are read and ready to
    be queried.

    **Methods**

    :``__getitem__``:              Return a parameter's value.
    :``__init__``:                 Initialize and return a ``Parameters``
                                   object.
    :``add_configuration_file``:   Add a file path to be searched for parameter
                                   values.
    :``add_parameter``:            Add a parameter to ``Parameters`` object.
    :``parse``:                    Prepare ``Parameters`` for queries and ensure
                                   parameter values can be found.
    :``read_configuration_files``: Read all configuration files' values.

    **Properties**

    :``defaults``:            Dictionary mapping parameter name to default
                              value.  Default: {}
    :``parameters``:          Dictionary mapping parameter name to parameter
                              arguments (arguments passed to ``add_parameter``).
                              Default: {}.
    :``grouped_parameters``:  Dictionary mapping parameter group to parameter
                              dictionary (see parameters property).  Default:
                              { 'default': {} }.
    :``configuration_files``: Dictionary mapping configuration file path to an
                              active ``ConfigParser.ConfigParser``.  Default:
                              {}.
    :``groups``:              Set of all parameter groups.  Always includes at
                              least the 'default' group.  Default:
                              set(['default']).
    :``parsed``:              True if ``Parameters`` has been parsed with the
                              ``parse`` method; otherwise, False.  Default:
                              False.

    **Example**

    Basic ``Parameters`` usage has four stages:

    1. Instantiate ``Parameters`` (cf. ``__init__``)::

           p = Parameters()

    2. Add parameters (cf. ``add_parameter``)::

           p.add_parameter(options = [ '--foo' ])

    3. Parse (cf. ``parse``)::

           p.parse()

    4. Query (cf. ``__getitem__``)::

           p['foo']

    """

    def __init__(  # pylint: disable=too-many-arguments,too-many-locals
        self,
        prog: Optional[str] = None,
        usage: Optional[str] = None,
        description: Optional[str] = None,
        epilog: Optional[str] = None,
        parents: Optional[List[argparse.ArgumentParser]] = None,
        formatter_class: Any = argparse.HelpFormatter,
        prefix_chars: str = "-",
        fromfile_prefix_chars: Optional[str] = None,
        argument_default: Optional[Any] = None,
        conflict_handler: str = "error",
        add_help: bool = True,
        allow_abbrev: bool = True,
        group_prefix: bool = True,
    ) -> None:
        """Initialize and return a ``Parameters`` object.

        **Arguments**

        :``group_prefix``: If True, prefix command line arguments with the group
                           name (i.e. group ← 'foo' and long option ← '--bar'
                           will produce a replacement long option '--foo-bar');
                           otherwise, leave long options as they are specified.
                           Default: True.

        .. note::
            All other arguments are directly passed to
            ``argparse.ArgumentParser`` and are not used by ``Parameters``.

        """

        LOGGER.info("STARTING: initializing Parameters object")

        if parents is None:
            parents = []

        self.defaults: Dict = {}
        self.parameters: Dict = {}
        self.grouped_parameters: Dict[str, Dict] = {"default": {}}
        self.configuration_files: Dict = {}
        self.groups = set(["default"])
        self.parsed = False

        self._group_prefix = group_prefix

        self._default_parser = argparse.ArgumentParser(
            prog=prog,
            usage=usage,
            description=description,
            epilog=epilog,
            parents=parents,
            formatter_class=formatter_class,
            prefix_chars=prefix_chars,
            fromfile_prefix_chars=fromfile_prefix_chars,
            argument_default=argument_default,
            conflict_handler=conflict_handler,
            add_help=add_help,
            allow_abbrev=allow_abbrev,
        )

        self._group_parsers: Dict[str, argparse._ArgumentGroup] = {}  # pylint: disable=protected-access
        self._argument_namespace = argparse.Namespace()

        LOGGER.info("STOPPING: initializing Parameters object")

    def __getitem__(  # pylint: disable=too-many-branches,too-many-locals,too-many-statements
        self, parameter_name: str
    ) -> Any:
        """Return the value of the requested parameter (by name).

        Given the ``parameter_name``, this method returns the found value for
        that parameter.  All three sources are searched for values.  The
        expected value is returned from the highest precedence source containing
        a value.

        The ``parameter_name`` must be prefixed with the group name and a dot
        '.' (i.e. group.long_option where group is the group name and
        long_option is the longest option in the options for the parameter).
        The group name can be ommitted if the parameter is a member of the
        'default' group.  The ``parameter_name`` is insensitive to the
        difference between hyphens '-' and underscores '_'; thus these
        characters can be used interchangeably.

        **Arguments**

        :``parameter_name``: Name of the parameter whose value is returned.

        **Return**

        Highest precedent value found for the requested parameter.

        """

        parameter_name = parameter_name.replace("-", "_")

        LOGGER.info("finding value of %s", parameter_name)

        if parameter_name not in self.parameters:
            parameter_name = ".".join(["default", parameter_name])

            if parameter_name not in self.parameters:
                raise KeyError(parameter_name.replace("default.", "", 1))

        if not self.parsed:
            LOGGER.warning("retrieving values from unparsed Parameters")

            caller_frame = inspect.stack()[1]

            caller_module = inspect.getmodule(caller_frame[0])
            caller_function = caller_frame[3]
            caller_line = caller_frame[2]

            LOGGER.warning("called from %s.%s:%s", caller_module, caller_function, caller_line)

            warnings.warn("retrieving values from unparsed Parameters", RuntimeWarning)

        default = self.defaults.get(parameter_name)

        LOGGER.info("default: %s", default)

        LOGGER.debug(
            "self.paramters[%s][environment_prefix]: %s",
            parameter_name,
            self.parameters[parameter_name]["environment_prefix"],
        )

        environment_variable_name = "_".join(parameter_name.replace("default.", "", 1).split(".")).upper()

        if self.parameters[parameter_name]["environment_prefix"] is not None:
            environment_variable_name = (
                self.parameters[parameter_name]["environment_prefix"] + "_" + environment_variable_name
            )

        LOGGER.debug("environment variable: %s", environment_variable_name)

        value = os.environ.get(environment_variable_name, default)

        if value is not None:
            try:
                value = os.path.expandvars(value)
            except TypeError:
                pass

        LOGGER.info("environment: %s", value)

        configuration_value = default
        for configuration_file_name, configuration_file in self.configuration_files.items():
            LOGGER.info("searching %s", configuration_file_name)

            try:
                configuration_value = configuration_file.get(*parameter_name.split(".", 1))
            except (NoOptionError, NoSectionError):
                LOGGER.info("%s not found", parameter_name)
                continue

            LOGGER.info("value: %s", configuration_value)

        LOGGER.debug("configuration_value: %s", configuration_value)

        if configuration_value != default:
            value = configuration_value

        LOGGER.info("configuration: %s", value)

        argument_name = parameter_name

        if self._group_prefix:
            argument_name = argument_name.replace(".", "_", 1)
        else:
            _, argument_name = argument_name.split(".", 1)

        argument_name = argument_name.replace("default_", "", 1)

        argument_value = getattr(self._argument_namespace, argument_name, default)

        LOGGER.debug("argument_value: %s", argument_value)

        if argument_value != default:
            value = argument_value

        LOGGER.info("argument: %s", value)

        if value is not None:
            value = self.parameters[parameter_name]["type"](value)

        return value

    def add_configuration_file(self, file_name: str) -> None:
        """Register a file path from which to read parameter values.

        This method can be called multiple times to register multiple files for
        querying.  Files are expected to be ``ini`` formatted.

        No assumptions should be made about the order that the registered files
        are read and values defined in multiple files may have unpredictable
        results.

        **Arguments**

        :``file_name``: Name of the file to add to the parameter search.

        """

        LOGGER.info("adding %s to configuration files", file_name)

        if os.access(file_name, os.R_OK):
            self.configuration_files[file_name] = SafeConfigParser()
            self.configuration_files[file_name].read(file_name)
        else:
            LOGGER.warning("could not read %s", file_name)
            warnings.warn("could not read {}".format(file_name), ResourceWarning)

    def add_parameter(  # pylint: disable=too-many-arguments,too-many-locals,too-many-branches
        self,
        options: List[str],
        environment_prefix: Optional[str] = None,
        group: str = "default",
        only: Sequence[str] = ("environment", "configuration", "argument"),
        action: str = "store",
        nargs: Optional[Union[int, str]] = None,
        const: Optional[Any] = None,
        default: Optional[Any] = None,
        type: Optional[Callable[[str], Any]] = None,  # pylint: disable=redefined-builtin
        choices: Optional[List[str]] = None,
        required: bool = False,
        help: Optional[str] = None,  # pylint: disable=redefined-builtin
        metavar: Optional[str] = None,
        dest: Optional[str] = None,
    ) -> None:
        """Add the parameter to ``Parameters``.

        **Arguments**

        The arguments are lumped into two groups:``Parameters.add_parameter``
        and ``argparse.ArgumentParser.add_argument``.  Parameters that are only
        used by ``Parameters.add_parameter`` are removed before ``kwargs`` is
        passed directly to argparse.ArgumentParser.add_argument``.

        .. note::
            Once ``parse`` has been called ``Parameters.parsed`` will be True
            and it is inadvisable to add more parameters to the ``Parameters``.

        *``Parameters.add_parameter`` Arguments*

        :``environment_prefix``: Prefix to add when searching the environment
                                 for this parameter.  Default:
                                 os.path.basename(sys.argv[0]).
        :``group``:              Group (namespace or prefix) for parameter
                                 (corresponds to section name in configuration
                                 files).  Default: 'default'.
        :``options``:            REQUIRED.  The list of options to match for
                                 this parameter in argv.
        :``only``:               Iterable containing the components that this
                                 parameter applies to (i.e. 'environment',
                                 'configuration', 'argument').  Default:
                                 ('environment', 'configuration', 'argument').

        *``argparse.ArgumentParser.add_argument`` Arguments*

        :``name or flags``: Positional argument filled in by options keyword
                            argument.
        :``action``:        The basic type of action to be taken when this
                            argument is encountered at the command line.
        :``nargs``:         The number of command-line arguments that should be
                            consumed.
        :``const``:         A constant value required by some action and nargs
                            selections.
        :``default``:       The value produced if the argument is absent from
                            the command line.
        :``type``:          The type to which the command-line argument should
                            be converted.
        :``choices``:       A container of the allowable values for the
                            argument.
        :``required``:      Whether or not the command-line option may be
                            omitted (optionals only).
        :``help``:          A brief description of what the argument does.
        :``metavar``:       A name for the argument in usage messages.
        :``dest``:          The name of the attribute to be added to the object
                            returned by parse_args().

        """

        parameter_name = max(options, key=len).lstrip("-")
        if dest is not None:
            parameter_name = dest

        self.groups.add(group)

        parameter_name = ".".join([group, parameter_name]).lstrip(".").replace("-", "_")

        LOGGER.info("adding parameter %s", parameter_name)

        if self.parsed:
            LOGGER.warning("adding parameter %s after parse", parameter_name)
            warnings.warn("adding parameter {} after parse".format(parameter_name), RuntimeWarning)

        if environment_prefix is None:
            environment_prefix = os.path.basename(sys.argv[0])

        if type is None:
            # The lambda keeps the types unifiable.
            type = lambda x: str(x)  # pylint: disable=unnecessary-lambda

        self.parameters[parameter_name] = {
            "options": options,
            "environment_prefix": environment_prefix,
            "group": group,
            "only": only,
            "action": action,
            "nargs": nargs,
            "const": const,
            "default": default,
            "type": type,
            "choices": choices,
            "required": required,
            "help": help,
            "metavar": metavar,
            "dest": dest,
        }

        if self.parameters[parameter_name]["environment_prefix"] is not None:
            self.parameters[parameter_name]["environment_prefix"] = (
                self.parameters[parameter_name]["environment_prefix"].upper().replace("-", "_")
            )

        LOGGER.info("group: %s", group)

        self.grouped_parameters.setdefault(group, {}).setdefault(
            parameter_name.replace(group + ".", ""), self.parameters[parameter_name]
        )

        action_defaults = {
            "store": default,
            "store_const": const,
            "store_true": False,
            "store_false": True,
            "append": [],
            "append_const": [],
            "count": 0,
        }

        self.defaults[parameter_name] = action_defaults[action]

        LOGGER.info("default value: %s", default)

        if "argument" in only:
            if group not in self._group_parsers:
                self._group_parsers[group] = self._default_parser.add_argument_group(group)

            add_argument_to: Callable[
                [Union[argparse.ArgumentParser, argparse._ArgumentGroup]],  # pylint: disable=protected-access
                functools.partial[argparse.Action],
            ] = lambda x: functools.partial(
                x.add_argument, *options, action=action, default=default, required=required, help=help
            )

            if group == "default":
                add_argument = add_argument_to(self._default_parser)
            else:
                if self._group_prefix:
                    long_option = max(options, key=len)

                    options.remove(long_option)
                    options.append(long_option.replace("--", "--" + group.replace("_", "-") + "-"))

                    LOGGER.debug("options: %s", options)

                add_argument = add_argument_to(self._group_parsers[group])

            if nargs is not None:
                add_argument = functools.partial(add_argument, nargs=nargs)

            if const is not None:
                add_argument = functools.partial(add_argument, const=const)

            if type is not None and action in ["store", "append"]:
                add_argument = functools.partial(add_argument, type=type)

            if choices is not None:
                add_argument = functools.partial(add_argument, choices=choices)

            if metavar is not None:
                add_argument = functools.partial(add_argument, metavar=metavar)

            add_argument()

    def parse(self, only_known: bool = False) -> None:
        """Ensure all sources are ready to be queried.

        Parses ``sys.argv`` with the contained ``argparse.ArgumentParser`` and
        sets ``parsed`` to True if ``only_known`` is False.  Once ``parsed`` is
        set to True, it is inadvisable to add more parameters (cf.
        ``add_parameter``).  Also, if ``parsed`` is not set to True, retrieving
        items (cf. ``__getitem__``) will result in a warning that values are
        being retrieved from an uparsed Parameters.

        **Arguments**

        :``only_known``: If True, do not error or fail when unknown parameters
                         are encountered.

                         .. note::
                             If ``only_known`` is True, the ``--help`` and
                             ``-h`` options on the command line (``sys.argv``)
                             will be ignored during parsing as it is unexpected
                             that these parameters' default behavior would be
                             desired at this stage of execution.

        """

        self.parsed = not only_known or self.parsed

        LOGGER.info("parsing parameters")

        LOGGER.debug("sys.argv: %s", sys.argv)

        if only_known:
            args = [_ for _ in copy.copy(sys.argv) if not re.match("-h|--help", _)]

            self._default_parser.parse_known_args(args=args, namespace=self._argument_namespace)
        else:
            self._default_parser.parse_args(namespace=self._argument_namespace)

    def read_configuration_files(self) -> None:
        """Explicitly read the configuration files.

        Reads all configuration files in this Parameters object.

        .. note::

           The order that the configuration files are read is not guaranteed.

        """

        for file_name, configuration_parser in self.configuration_files.items():
            if os.access(file_name, os.R_OK):
                configuration_parser.read(file_name)
            else:
                LOGGER.warning("could not read %s", file_name)
                warnings.warn("could not read {}".format(file_name), ResourceWarning)
