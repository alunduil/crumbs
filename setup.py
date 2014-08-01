# Copyright (C) 2014 by Alex Brandt <alunduil@alunduil.com>
#
# crumbs is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

from setuptools import setup
from codecs import open

from crumbs import information

PARAMS = {}

PARAMS['name'] = information.NAME
PARAMS['version'] = information.VERSION
PARAMS['description'] = information.DESCRIPTION

with open('README.rst', 'r', encoding = 'utf-8') as fh:
    PARAMS['long_description'] = fh.read()

PARAMS['url'] = information.URL
PARAMS['author'] = information.AUTHOR
PARAMS['author_email'] = information.AUTHOR_EMAIL
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

PARAMS['packages'] = [
    'crumbs',
]

PARAMS['install_requires'] = []

PARAMS['extras_require'] = {
    'inotify': [
        'pyinotify',
    ],
}

PARAMS['test_suite'] = 'nose.collector'
PARAMS['tests_require'] = [
    'coverage',
    'mock',
    'nose',
]

PARAMS['data_files'] = [
    ('share/doc/{P[name]}-{P[version]}'.format(P = PARAMS), [
        'README.rst',
    ]),
]

setup(**PARAMS)
