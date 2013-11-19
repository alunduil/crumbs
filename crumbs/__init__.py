# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 by Alex Brandt <alunduil@alunduil.com>
#
# crumbs is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import argparse
import copy
import os
import sys
import re

try:
    from configparser import SafeConfigParser
    from configparser import NoOptionError
    from configparser import NoSectionError
except ImportError:
    from ConfigParser import SafeConfigParser
    from ConfigParser import NoOptionError
    from ConfigParser import NoSectionError

logger = logging.getLogger(__name__)

class Parameters(object):
    def __init__(self, *args, **kwargs):
        '''Initialize Parameters with the given items.

        This initializes a blank set of parameters to which parameters and
        configuration files may be added.

        This object keeps track of multiple configuration files and multiple
        groupings of parameters.

        Arguments
        ---------

        :``group_prefix``: Prefix command line arguments with the group name if
                           this is True; otherwise, ignore groups on command
                           line arguments.  Default: True.

        Any other passed arguments are picked up by wildcards (*args and
        **kwargs).  These are passed directly to an instance of ArgumentParser
        for initialization.

        '''

        logger.info('initializing Parameters object')

        self.defaults = {}
        self.parameters = {}
        self.configuration_files = {}
        self.groups = set([ 'default' ])
        self.parsed = False

        self._group_prefix = kwargs.pop('group_prefix', True)

        self._group_parsers = { 'default': argparse.ArgumentParser(*args, **kwargs) }
        self._argument_namespace = argparse.Namespace()

    def add_parameter(self, **kwargs):
        '''Add the specified components as a parameter.

        The components mostly line up with the argparse arguments (outlined
        below).  There are a couple of extra possible arguments that we utilize
        and everything else is discarded without being inspected.

        Arguments
        ---------

        The arguments are lumped into two groups which are inspected for the
        listed items.  These are passed to ArgumentParser.add_argument after
        removing the specific items for Parameters.

        Parameters.add_parameter Arguments
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

        :``group``:   Namespace or section (in configuration file terms) for
                      this parameter.
        :``options``: The list of options to match for this parameter in argv.
        :``only``:    Iterable containing the components that this parameter
                      applies to (i.e. environment, configuration, argument).

        ArgumentParser.add_argument Arguments
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

        :``name or flags``: Read from kwargs[options].
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

        self.parameters[parameter_name] = copy.copy(kwargs)
        self.parameters[parameter_name]['group'] = group
        self.parameters[parameter_name]['type'] = kwargs.get('type', str)

        logger.info('group: %s', group)

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

    def add_configuration_file(self, file_name):
        '''Add a configuration file to be searched for parameters.

        The configuration file name passed will be added to the parameter
        search space.  The file is expected to be an ini style file as we
        utilize the built-in configparser module to actually read the values
        from the file.

        The files are not searched in any particular order and duplicates take
        the last value found in the last file it was present.

        .. note::
            Perhaps we should change this so that the ordering is the reverse
            order that the files will be searched?

        Arguments
        ---------

        :``file_name``: Name of the file to add to the parameter search.

        '''

        logger.info('adding %s to configuration files', file_name)

        if os.access(file_name, os.R_OK):
            self.configuration_files[file_name] = SafeConfigParser()
            self.configuration_files[file_name].read(file_name)
        else:
            logger.warn('could not read %s', file_name)

    def parse(self, only_known = False):
        '''Parse the sources and prepare them for searching.

        This ensures that the sources (environment, configuration(s), and
        arguments) are in a state that we can begin retrieving items.  If the
        ``only_known`` is ``True`` then we don't concern ourself with
        parameters that were specified that we don't know about yet.  This
        allows us to get parameters that tell us where other parameters might
        be hiding (i.e. configuration files).

        Arguments
        ---------

        :``only_known``: Parse only the parameters we have record of if this is
                         set to True; otherwise, parse everything and do full
                         error handling of parameters

        .. note::
            Once parse is called (without ``only_known``) it is inadvisable to
            add any more parameters to the structure.

         This marks the parsed property to true if full parsing has or is
         occurring.  parsed will be marked according to the following logic::
            parsed ← ( only_known → parsed )

        .. note::
            There is nothing special about parsing configuration files or the
            environment and these lookups happen against the live (when they
            were created) values contained in these sources.

        If ``only_known`` is ``True``, the ``--help`` or ``-h`` options will be
        ignored during this parsing so that the parser can be fully loaded in
        the event that you want to use parameters before you've finished adding
        all of your required parameters.

        '''

        self.parsed = not only_known or self.parsed

        logger.info('parsing parameters')

        logger.debug('sys.argv: %s', sys.argv)

        if only_known:
            args = [ _ for _ in copy.copy(sys.argv) if not re.match('-h|--help', _) ]

            self._group_parsers['default'].parse_known_args(args = args, namespace = self._argument_namespace)
        else:
            self._group_parsers['default'].parse_args(namespace = self._argument_namespace)

    def __getitem__(self, parameter_name):
        '''Retrieve the specified parameter from this instance of Parameters.

        There are a couple of niceties added to this interface that are shown in
        detail in the examples below.  The niceties include the following:

        * the '-' and '_' separators in parameter names are interchangeable and
          the user does not need to be concerned about the similarity of foo-bar
          and foor_bar as a result.  Both of these names if requested will
          return the same stored value if it exists.
        * if the key cannot be found as written the group of default will be
          searched.  This means that if the user passes in the name foo but that
          name is not present as is, the name default.foo will be tried.  This
          also means that if a seemingly scoped name (i.e. foo.bar) is passed,
          we will try the default prefixed name (i.e. defautl.foo.bar).

        Arguments
        ---------

        :``parameter_name``: Name to retrive the value from the variuos sources

        Returns
        -------

        Value of the given ``parameter_name`` from the highest priority source.

        Precedence of Sources
        ---------------------

        The sources have a certain precedence that values may come from (this is
        most apparent when the same name is defined in multiple sources).  That
        precedence is the following:

        :argument:      Argument vector or command line arguments
        :configuration: Configuration files (all of equal precedence) (see
                        add_configuration_file)
        :environment:   Environment variables given to every process
        :default:       Defined default values for the parameters added

        These will be searched in reverse order as the source closest to the top
        of the list will win and its value will be returned.

        Examples
        --------

        Names can be prefixed with the argument's group if it had one (i.e.
        foo.bar for group foo with option bar).  If options for a parameter were
        specified with a separator (hyphen, '-', or underscore, '_') this
        separator can be specified as either character with no loss of meaning.

        .. note::
            The last remark means that the names foo.bar-baz and foo.bar_baz are
            not unique.

        Environment variables relate to parameter names in a mostly obviuos way:

        * foo.bar → ARGV0_FOO_BAR
        * bar → ARGV0_BAR

        .. note::
            Parameters in the default group do not have their group added to the
            environment variables' name while those that are in other groups do.

        Of course, in the preceeding examples, ARGV0 is replaced with the name
        for the invoking application, sys.argv[0].

        '''

        parameter_name = parameter_name.replace('-', '_')

        logger.info('finding value of %s', parameter_name)

        if parameter_name not in self.parameters:
            parameter_name = '.'.join([ 'default', parameter_name ])

            if parameter_name not in self.parameters:
                raise KeyError(parameter_name.replace('default.', '', 1))

        if not self.parsed:
            logger.warn('retrieving values from unparsed Parameters')

        default = self.defaults.get(parameter_name)

        logger.info('default: %s', default)

        value = os.environ.get('_'.join([ sys.argv[0] ] + parameter_name.replace('default.', '', 1).split('.')).upper(), default)

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

        return self.parameters[parameter_name]['type'](value)
