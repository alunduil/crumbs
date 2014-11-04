# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 by Alex Brandt <alunduil@alunduil.com>
#
# crumbs is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import os

from setuptools import setup
from codecs import open

with open(os.path.join('crumbs', 'information.py'), 'r', encoding = 'utf-8') as fh:
    exec(fh.read(), globals(), locals())

PARAMS = {}

PARAMS['name'] = NAME  # flake8: noqa — provided by exec
PARAMS['version'] = VERSION  # flake8: noqa — provided by exec
PARAMS['description'] = DESCRIPTION  # flake8: noqa — provided by exec

with open('README.rst', 'r', encoding = 'utf-8') as fh:
    PARAMS['long_description'] = fh.read()

PARAMS['url'] = URL  # flake8: noqa — provided by exec
PARAMS['author'] = AUTHOR  # flake8: noqa — provided by exec
PARAMS['author_email'] = AUTHOR_EMAIL  # flake8: noqa — provided by exec
PARAMS['license'] = LICENSE  # flake8: noqa — provided by exec

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
    'nose',
]

PARAMS['data_files'] = [
    ('share/doc/{P[name]}-{P[version]}'.format(P = PARAMS), [
        'README.rst',
    ]),
]

setup(**PARAMS)
