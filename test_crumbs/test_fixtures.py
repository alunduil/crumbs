# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 by Alex Brandt <alunduil@alunduil.com>
#
# crumbs is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import copy
import logging

logger = logging.getLogger(__name__)


PARAMETERS = {
    'valid': {},
}


def add_parameter(parameters, parameter):
    '''Add the paramter to the parameters dictionary.

    Arguments
    ---------

    :parameter:  dictionary with single parameter description (contains `input`,
                 `default`, `parameter`, `group`)
    :parameters: dictionary in which to store the parameter

    '''

    logger.debug('parameter[input]: %s', parameter['input'])
    parameters.setdefault('inputs', []).append(parameter['input'])

    logger.debug('parameter[default]: %s', parameter['default'])
    parameters.setdefault('defaults', {}).update(parameter['default'])

    logger.debug('parameter[parameter]: %s', parameter['parameter'])
    parameters.setdefault('parameters', {}).update(copy.deepcopy(parameter['parameter']))

    logger.debug('parameter[group]: %s', parameter['parameter'])
    parameters.setdefault('groups', set()).add(parameter['group'])

    for name in parameter['parameter'].keys():
        parameter['parameter'][name.split('.', 1)[-1]] = parameter['parameter'].pop(name)

    parameters.setdefault('grouped_parameters', {}).setdefault(parameter['group'], {}).update(parameter['parameter'])


add_parameter(PARAMETERS['valid'], {
    'input': {
        'group': 'bar',
        'options': [ '--foo' ],
    },
    'default': {
        'bar.foo': None,
    },
    'parameter': {
        'bar.foo': {
            'environment_prefix': 'NOSETESTS',
            'group': 'bar',
            'options': [ '--foo' ],
            'type': str,
        },
    },
    'group': 'bar',
})

add_parameter(PARAMETERS['valid'], {
    'input': {
        'group': 'under_score',
        'options': [ '--group' ],
    },
    'default': {
        'under_score.group': None,
    },
    'parameter': {
        'under_score.group': {
            'environment_prefix': 'NOSETESTS',
            'group': 'under_score',
            'options': [ '--group' ],
            'type': str,
        },
    },
    'group': 'under_score',
})

add_parameter(PARAMETERS['valid'], {
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
            'environment_prefix': 'NOSETESTS',
            'group': 'foo',
            'options': [ '--bar', '-b' ],
            'default': 'baz',
            'type': str,
            'help': 'assistance is futile',
        },
    },
    'group': 'foo',
})

add_parameter(PARAMETERS['valid'], {
    'input': {
        'group': 'default',
        'options': [ '--baz' ],
        'action': 'store_true',
        'help': 'assistance is futile',
    },
    'default': {
        'default.baz': False,
    },
    'parameter': {
        'default.baz': {
            'environment_prefix': 'NOSETESTS',
            'group': 'default',
            'options': [ '--baz' ],
            'type': str,
            'action': 'store_true',
            'help': 'assistance is futile',
        },
    },
    'group': 'default',
})

add_parameter(PARAMETERS['valid'], {
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
            'environment_prefix': 'NOSETESTS',
            'group': 'default',
            'options': [ '--qux', '-q' ],
            'type': str,
            'default': 'foo',
            'help': 'assistance is futile',
        },
    },
    'group': 'default',
})

add_parameter(PARAMETERS['valid'], {
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
            'environment_prefix': 'NOSETESTS',
            'group': 'default',
            'options': [ 'foobar' ],
            'type': str,
            'nargs': '*',
            'help': 'assistance is futile',
        },
    },
    'group': 'default',
})

add_parameter(PARAMETERS['valid'], {
    'input': {
        'options': [ '--foobaz' ],
        'dest': 'quxbaz',
    },
    'default': {
        'default.quxbaz': None,
    },
    'parameter': {
        'default.quxbaz': {
            'environment_prefix': 'NOSETESTS',
            'group': 'default',
            'options': [ '--foobaz' ],
            'type': str,
            'dest': 'quxbaz',
        },
    },
    'group': 'default',
})

add_parameter(PARAMETERS['valid'], {
    'input': {
        'options': [ '--environment-only' ],
        'only': [ 'environment' ],
    },
    'default': {
        'default.environment_only': None,
    },
    'parameter': {
        'default.environment_only': {
            'environment_prefix': 'NOSETESTS',
            'group': 'default',
            'options': [ '--environment-only' ],
            'type': str,
            'only': [ 'environment' ],
        },
    },
    'group': 'default',
})

add_parameter(PARAMETERS['valid'], {
    'input': {
        'options': [ '--prefixed-environment' ],
        'only': [ 'environment' ],
        'environment_prefix': 'crumbs',
    },
    'default': {
        'default.prefixed_environment': None,
    },
    'parameter': {
        'default.prefixed_environment': {
            'environment_prefix': 'CRUMBS',
            'group': 'default',
            'options': [ '--prefixed-environment' ],
            'type': str,
            'only': [ 'environment' ],
        },
    },
    'group': 'default',
})
