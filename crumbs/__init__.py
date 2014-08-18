# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 by Alex Brandt <alunduil@alunduil.com>
#
# crumbs is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

'''Provides an easy to use multi-source parameter container.

:``Parameters``:        Queryable collection of parameters whose values are set
                        by the user.
:``information``:       Miscellaneous information about crumbs (i.e. version).
:``_pyinotify_loaded``: Not technically publically exposed but evaluates as True
                        if pyinotify is successfully loaded and False if not.

'''

import logging
import argparse
import copy
import os
import sys
import re
import warnings

try:
    from configparser import SafeConfigParser
    from configparser import NoOptionError
    from configparser import NoSectionError
except ImportError:
    from ConfigParser import SafeConfigParser
    from ConfigParser import NoOptionError
    from ConfigParser import NoSectionError

logger = logging.getLogger(__name__)
try:
    logger.addHandler(logging.NullHandler())
except:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

    logger.addHandler(NullHandler())

_pyinotify_loaded = True
try:
    import pyinotify
except ImportError:
    logger.warn('could not load pyinotify—all inotify behavior ignored')
    _pyinotify_loaded = False

try:
    import builtins
except ImportError:
    import __builtin__ as builtins

if 'ResourceWarning' not in vars(builtins):
    class ResourceWarning(Warning):
        pass


class Parameters(object):
    '''Queryable collection of parameters whose values are set by the user.

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

    Methods
    -------

    :``__getitem__``:            Return a parameter's value.
    :``__init__``:               Initialize and return a ``Parameters`` object.
    :``add_configuration_file``: Add a file path to be searched for parameter
                                 values.
    :``add_parameter``:          Add a parameter to ``Parameters`` object.
    :``parse``:                  Prepare ``Parameters`` for queries and ensure
                                 parameter values can be found.

    Properties
    ----------

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

    Example
    -------

    Basic ``Parameters`` usage has four stages:

    1. Instantiate ``Parameters`` (cf. `__init__`__)
    >>> p = Parameters()

    2. Add parameters (cf. `add_parameter`__)
    >>> p.add_parameter(options = [ '--foo' ])

    3. Parse (cf. `parse`__)
    >>> p.parse()

    4. Query (cf. `__getitem__`__)
    >>> p['foo']

    '''

    def __init__(self, *args, **kwargs):
        '''Initialize and return a ``Parameters`` object.

        Arguments
        ---------

        :``group_prefix``: If True, prefix command line arguments with the group
                           name (i.e. group ← 'foo' and long option ← '--bar'
                           will produce a replacement long option '--foo-bar');
                           otherwise, leave long options as they are specified.
                           Default: True.
        :``inotify``:      Use pyinotify (if present) to re-read configuration
                           files as they are modified.  Default: False.

        .. note::
            All other arguments are directly passed to
            ``argparse.ArgumentParser`` and are not used by ``Parameters``.

        '''

        logger.info('STARTING: initializing Parameters object')

        self.defaults = {}
        self.parameters = {}
        self.grouped_parameters = { 'default': {} }
        self.configuration_files = {}
        self.groups = set([ 'default' ])
        self.parsed = False

        self._group_prefix = kwargs.pop('group_prefix', True)

        self._inotify = kwargs.pop('inotify', False) and _pyinotify_loaded

        self._group_parsers = { 'default': argparse.ArgumentParser(*args, **kwargs) }
        self._argument_namespace = argparse.Namespace()

        if self._inotify:
            self._watch_manager = pyinotify.WatchManager()

            class EventHandler(pyinotify.ProcessEvent):
                def my_init(self, configuration_files):
                    self.configuration_files = configuration_files

                def process_IN_MODIFY(self, event):
                    logger.info('re-reading %s', event.pathname)

                    self.configuration_files[event.pathname].read(event.pathname)

            self._notifier = pyinotify.Notifier(self._watch_manager, EventHandler(configuration_files = self.configuration_files))
            self._notifier.coalesce_events()

        logger.info('STOPPING: initializing Parameters object')

    def __del__(self):
        '''Prepare for garbage collection.

        Attempt to stop the ``pyinotify.Notifier`` if inotify is in use.

        '''

        if self._inotify and self._notifier is not None:
            self._notifier.stop()

    def __getitem__(self, parameter_name):
        '''Return the value of the requested parameter (by name).

        Given the ``parameter_name``, this method returns the found value for
        that parameter.  All three sources are searched for values.  The
        expected value is returned from the hight precedence source containing
        a value.

        The ``parameter_name`` must be prefixed with the group name and a dot
        '.' (i.e. group.long_option where group is the group name and
        long_option is the longest option in the options for the parameter).
        The group name can be ommitted if the parameter is a member of the
        'default' group.  The ``parameter_name`` is insensitive to the
        difference between hyphens '-' and underscores '_'; thus these
        characters can be used interchangeably.

        Arguments
        ---------

        :``parameter_name``: Name of the parameter whose value is returned.

        Return
        ------

        Highest precedent value found for the requested parameter.

        '''

        if self._inotify and self._notifier.check_events(timeout = 10):
            logger.debug('events available: %s', self._notifier.check_events())
            logger.info('processing inotifications')
            self._notifier.read_events()
            self._notifier.process_events()

        parameter_name = parameter_name.replace('-', '_')

        logger.info('finding value of %s', parameter_name)

        if parameter_name not in self.parameters:
            parameter_name = '.'.join([ 'default', parameter_name ])

            if parameter_name not in self.parameters:
                raise KeyError(parameter_name.replace('default.', '', 1))

        if not self.parsed:
            logger.warn('retrieving values from unparsed Parameters')
            warnings.warn('retrieving values from unparsed Parameters', RuntimeWarning)

        default = self.defaults.get(parameter_name)

        logger.info('default: %s', default)

        logger.debug('self.paramters[%s][environment_prefix]: %s', parameter_name, self.parameters[parameter_name]['environment_prefix'])

        _ = '_'.join(parameter_name.replace('default.', '', 1).split('.')).upper()

        if self.parameters[parameter_name]['environment_prefix'] is not None:
            _ = self.parameters[parameter_name]['environment_prefix'] + '_' + _

        logger.debug('environment variable: %s', _)

        value = os.environ.get(_, default)
        try:
            value = os.path.expandvars(value)
        except TypeError:
            pass

        logger.info('environment: %s', value)

        configuration_value = default
        for configuration_file_name, configuration_file in self.configuration_files.items():
            logger.info('searching %s', configuration_file_name)

            try:
                configuration_value = configuration_file.get(*parameter_name.split('.', 1))
            except (NoOptionError, NoSectionError):
                logger.info('%s not found', parameter_name)
                continue

            logger.info('value: %s', configuration_value)

        logger.debug('configuration_value: %s', configuration_value)

        if configuration_value != default:
            value = configuration_value

        logger.info('configuration: %s', value)

        argument_name = parameter_name

        if self._group_prefix:
            argument_name = argument_name.replace('.', '_', 1)
        else:
            _, argument_name = argument_name.split('.', 1)

        argument_name = argument_name.replace('default_', '', 1)

        argument_value = getattr(self._argument_namespace, argument_name, default)

        logger.debug('argument_value: %s', argument_value)

        if argument_value != default:
            value = argument_value

        logger.info('argument: %s', value)

        if value is not None:
            value = self.parameters[parameter_name]['type'](value)

        return value

    def add_configuration_file(self, file_name):
        '''Register a file path from which to read parameter values.

        This method can be called multiple times to register multiple files for
        querying.  Files are expected to be ``ini`` formatted.

        No assumptions should be made about the order that the registered files
        are read and values defined in multiple files may have unpredictable
        results.

        Arguments
        ---------

        :``file_name``: Name of the file to add to the parameter search.

        '''

        logger.info('adding %s to configuration files', file_name)

        if file_name not in self.configuration_files and self._inotify:
            self._watch_manager.add_watch(file_name, pyinotify.IN_MODIFY)

        if os.access(file_name, os.R_OK):
            self.configuration_files[file_name] = SafeConfigParser()
            self.configuration_files[file_name].read(file_name)
        else:
            logger.warn('could not read %s', file_name)
            warnings.warn('could not read {}'.format(file_name), ResourceWarning)

    def add_parameter(self, **kwargs):
        '''Add the parameter to ``Parameters``.

        Arguments
        ---------

        The arguments are lumped into two groups:``Parameters.add_parameter``
        and ``argparse.ArgumentParser.add_argument``.  Parameters that are only
        used by ``Parameters.add_parameter`` are removed before ``kwargs`` is
        passed directly to argparse.ArgumentParser.add_argument``.

        .. note::
            Once ``parse`` has been called ``Parameters.parsed`` will be True
            and it is inadvisable to add more parameters to the ``Parameters``.

        ``Parameters.add_parameter`` Arguments
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

        ``argparse.ArgumentParser.add_argument`` Arguments
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

        '''

        parameter_name = max(kwargs['options'], key = len).lstrip('-')

        if 'dest' in kwargs:
            parameter_name = kwargs['dest']

        group = kwargs.pop('group', 'default')
        self.groups.add(group)

        parameter_name = '.'.join([ group, parameter_name ]).lstrip('.').replace('-', '_')

        logger.info('adding parameter %s', parameter_name)

        if self.parsed:
            logger.warn('adding parameter %s after parse', parameter_name)
            warnings.warn('adding parameter {} after parse'.format(parameter_name), RuntimeWarning)

        self.parameters[parameter_name] = copy.copy(kwargs)
        self.parameters[parameter_name]['group'] = group
        self.parameters[parameter_name]['type'] = kwargs.get('type', str)
        self.parameters[parameter_name]['environment_prefix'] = kwargs.pop('environment_prefix', os.path.basename(sys.argv[0]))

        if self.parameters[parameter_name]['environment_prefix'] is not None:
            self.parameters[parameter_name]['environment_prefix'] = self.parameters[parameter_name]['environment_prefix'].upper().replace('-', '_')

        logger.info('group: %s', group)

        self.grouped_parameters.setdefault(group, {}).setdefault(parameter_name.replace(group + '.', ''), self.parameters[parameter_name])

        action_defaults = {
            'store': kwargs.get('default'),
            'store_const': kwargs.get('const'),
            'store_true': False,
            'store_false': True,
            'append': [],
            'append_const': [],
            'count': 0,
        }

        self.defaults[parameter_name] = action_defaults[kwargs.get('action', 'store')]

        logger.info('default value: %s', kwargs.get('default'))

        if 'argument' in kwargs.pop('only', [ 'argument' ]):
            if group not in self._group_parsers:
                self._group_parsers[group] = self._group_parsers['default'].add_argument_group(group)

            if self._group_prefix and group != 'default':
                long_option = max(kwargs['options'], key = len)

                kwargs['options'].remove(long_option)
                kwargs['options'].append(long_option.replace('--', '--' + group.replace('_', '-') + '-'))

                logger.debug('options: %s', kwargs['options'])

            self._group_parsers[group].add_argument(*kwargs.pop('options'), **kwargs)

    def parse(self, only_known = False):
        '''Ensure all sources are ready to be queried.

        Parses ``sys.argv`` with the contained ``argparse.ArgumentParser`` and
        sets ``parsed`` to True if ``only_known`` is False.  Once ``parsed`` is
        set to True, it is inadvisable to add more parameters (cf.
        ``add_parameter``_).  Also, if ``parsed`` is not set to True, retrieving
        items (cf. ``__getitem__``_) will result in a warning that values are
        being retrieved from an uparsed Parameters.

        Arguments
        ---------

        :``only_known``: If True, do not error or fail when unknown parameters
                         are encountered.

                         .. note::
                             If ``only_known`` is True, the ``--help`` and
                             ``-h`` options on the command line (``sys.argv``)
                             will be ignored during parsing as it is unexpected
                             that these parameters' default behavior would be
                             desired at this stage of execution.

        '''

        self.parsed = not only_known or self.parsed

        logger.info('parsing parameters')

        logger.debug('sys.argv: %s', sys.argv)

        if only_known:
            args = [ _ for _ in copy.copy(sys.argv) if not re.match('-h|--help', _) ]

            self._group_parsers['default'].parse_known_args(args = args, namespace = self._argument_namespace)
        else:
            self._group_parsers['default'].parse_args(namespace = self._argument_namespace)
