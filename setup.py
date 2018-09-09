# -*- coding: utf-8 -*-

import os

from codecs import open
from setuptools import setup

readme=""
with open("README.rst", 'r', encoding="utf-8") as fh:
    readme=fh.read()

setup(
    name="crumbs",
    version="2.1.0",
    description="Generalized all-in-one parameters module.",
    long_descpription=readme,
    url="https://github.com/alunduil/crumbs",

    author="Alex Brandt",
    author_email="alunduil@gmail.com",

    license="MIT",

    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Libraries",
    ],

    keywords=[
        "arguments",
        "configuration",
        "crumbs",
        "environment",
        "parameters",
    ],

    packages=[
        "crumbs",
    ],

    install_requires=[
        "pyinotify",
    ],

    tests_require=[
        "pytest",
    ],
)
