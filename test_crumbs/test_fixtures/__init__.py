# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 by Alex Brandt <alunduil@alunduil.com>
#
# crumbs is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging

logger = logging.getLogger(__name__)

PARAMETERS = []

def extract_dictionary(iterable, extraction_key):
    '''Extract the specified key from the provided iterable as a dict.

    In this module, we create a list of dictionaries that contain components
    that can be joined into a distinct dictionary.  Look through PARAMETERS for
    `default` or `parameter` keys in the contained dictionaries.  This function
    extracts all of the individual keys requested (i.e. `default` or
    `parameter`) and crafts the merged dictionary from these individual items.

    Parameters
    ^^^^^^^^^^

    :iterable:       Iterable to search for the key provided and reconstruct the
                     desired dictionary.
    :extraction_key: Key to extract dictionaries that will be reconstructed
                     into the resulting dictionary.  This key must point at
                     dict items in the iterable.

    Examples
    ^^^^^^^^

    >>> extract_dictionary([ { 'a': { 1: 1 } }, { 'a': { 2: 2 } } ], 'a')
    { 1: 1, 2: 2 }

    '''

    result = {}

    for _ in iterable:
        result.update(_[extraction_key])

    return result

def extract_set(iterable, extraction_key):
    '''Extract the specified key from the provided dictionary as a set.

    In this module, we create a list of dictionaries that contain components
    that can be joined into a distinct set.  Look through PARAMETERS for
    `group` keys in the contained dictionaries.  This function extracts all of
    the individual keys requested (i.e. `group`) and crafts the merged set from
    these individual items.

    Parameters
    ^^^^^^^^^^

    :iterable:       Iterable to search for the key provided and reconstruct the
                     desired set.
    :extraction_key: Key to extract items that will be reconstructed into the
                     resulting set.

    Examples
    ^^^^^^^^

    >>> extract_set([ { 'a': 1 }, { 'a': 2 }, { 'a': 1 } ], 'a')
    set([ 1, 2 ])

    '''

    result = set()

    for _ in iterable:
        result.add(_[extraction_key])

    return result

PARAMETERS.append(
        {
            'input': {
                'group': 'foo',
                'options': [ '--bar', '-b' ],
                'default': 'baz',
                'type': str,
                'help': 'assistance is futile',
                },
            'default': {
                'foo.bar': 'baz',
                },
            'parameter': {
                'foo.bar': {
                    'group': 'foo',
                    'options': [ '--bar', '-b' ],
                    'default': 'baz',
                    'type': str,
                    'help': 'assistance is futile',
                    },
                },
            'group': 'foo',
            },
        )

PARAMETERS.append(
        {
            'input': {
                'group': 'default',
                'options': [ '--baz', '-b' ],
                'action': 'store_true',
                'help': 'assistance is futile',
                },
            'default': {
                'default.baz': False,
                },
            'parameter': {
                'default.baz': {
                    'group': 'default',
                    'options': [ '--baz', '-b' ],
                    'type': str,
                    'action': 'store_true',
                    'help': 'assistance is futile',
                    },
                },
            'group': 'default',
            },
        )

PARAMETERS.append(
        {
            'input': {
                'options': [ '--qux', '-q' ],
                'default': 'foo',
                'help': 'assistance is futile',
                },
            'default': {
                'default.qux': 'foo',
                },
            'parameter': {
                'default.qux': {
                    'group': 'default',
                    'options': [ '--qux', '-q' ],
                    'type': str,
                    'default': 'foo',
                    'help': 'assistance is futile',
                    },
                },
            'group': 'default',
            },
        )

PARAMETERS.append(
        {
            'input': {
                'options': [ 'foobar' ],
                'nargs': '*',
                'help': 'assistance is futile',
                },
            'default': {
                'default.foobar': None,
                },
            'parameter': {
                'default.foobar': {
                    'group': 'default',
                    'options': [ 'foobar' ],
                    'type': str,
                    'nargs': '*',
                    'help': 'assistance is futile',
                    },
                },
            'group': 'default',
            },
        )

PARAMETERS.append(
        {
            'input': {
                'options': [ '--foobaz' ],
                'dest': 'quxbaz',
                },
            'default': {
                'default.quxbaz': None,
                },
            'parameter': {
                'default.quxbaz': {
                    'group': 'default',
                    'options': [ '--foobaz' ],
                    'type': str,
                    'dest': 'quxbaz',
                    },
                },
            'group': 'default',
            },
        )

PARAMETERS.append(
        {
            'input': {
                'options': [ '--environment-only' ],
                'only': [ 'environment' ],
                },
            'default': {
                'default.environment_only': None,
                },
            'parameter': {
                'default.environment_only': {
                    'group': 'default',
                    'options': [ '--environment-only' ],
                    'type': str,
                    'only': [ 'environment' ],
                    },
                },
            'group': 'default',
            },
        )
