# Copyright (C) 2014 by Alex Brandt <alunduil@alunduil.com>
#
# crumbs is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import pip

from setuptools import setup

from crumbs import information

PARAMS = {}

PARAMS['name'] = information.NAME
PARAMS['version'] = information.VERSION
PARAMS['description'] = information.DESCRIPTION

with open('README.rst', 'r') as fh:
    PARAMS['long_description'] = fh.read()

PARAMS['author'] = information.AUTHOR
PARAMS['author_email'] = information.AUTHOR_EMAIL
PARAMS['url'] = information.URL
PARAMS['license'] = information.LICENSE

PARAMS['classifiers'] = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: Implementation :: CPython',
    'Topic :: Software Development :: Libraries',
]

PARAMS['keywords'] = [
    'crumbs',
    'parameters',
    'configuration',
    'environment',
    'arguments',
]

PARAMS['provides'] = [
    'crumbs',
]

PARAMS['install_requires'] = [
    'setuptools',
    'pip',
]

PARAMS['requires'] = [ str(_.req) for _ in pip.req.parse_requirements('requirements.txt') ]

PARAMS['extras_require'] = {
    'inotify': [
        'pyinotify',
    ],
}

PARAMS['tests_require'] = [ str(_.req) for _ in pip.req.parse_requirements('test_crumbs/requirements.txt') ]
PARAMS['test_suite'] = 'nose.collector'

PARAMS['packages'] = [
    'crumbs',
]

PARAMS['data_files'] = [
    ('share/doc/{P[name]}-{P[version]}'.format(P = PARAMS), [
        'README.rst',
    ]),
]

setup(**PARAMS)
