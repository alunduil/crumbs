# Copyright (C) 2013 by Alex Brandt <alunduil@alunduil.com>
#
# pmort is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import argparse
import copy

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

        Any passed arguments are picked up by wildcards (*args and **kwargs).
        These are passed directly to an instance of ArgumentParser for
        initialization.

        '''

        logger.info('initializing Parameters object')

        self.defaults = {}
        self.parameters = {}
        self.configuration_files = {}
        self.groups = set([ 'default' ])
        self.parsed = False

        self._group_parsers = { 'default': argparse.ArgumentParser(*args, **kwargs) }

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

        parameter_name = '.'.join([ group, parameter_name ]).lstrip('.')

        logger.info('adding parameter %s', parameter_name)

        if self.parsed:
            logger.warn('adding parameter %s after parse', parameter_name)

        self.parameters[parameter_name] = copy.copy(kwargs)
        self.parameters[parameter_name]['group'] = group

        logger.info('group: %s', group)

        actions = {
                'store': kwargs.get('default'),
                'store_const': kwargs.get('const'),
                'store_true': False,
                'store_false': True,
                'append': [],
                'append_const': [],
                'count': 0,
                }

        self.defaults[parameter_name] = actions[kwargs.get('action', 'store')]

        logger.info('default value: %s', kwargs.get('default'))

        if 'argument' in kwargs.pop('only', [ 'argument' ]):
            if group not in self._group_parsers:
                self._group_parsers[group] = self._group_parsers['default'].add_argument_group(group)

            self._group_parsers[group].add_argument(*kwargs.pop('options'), **kwargs)
