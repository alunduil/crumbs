Description
===========

Generalized all-in-one parameters module.

This package provides a single interface to environment variables', 
configuration files', and command line arguments' provided values.  The 
dictionary-like interface makes interacting with these, most of the time 
disparate, resources much simpler.  It also allows parameters' values to be set
in any of the three sources and selects an appropriate value when a parameter's
value is specified in multiple sources.  This way the most expected value,
according to the normal prcedence—command line arguments then configuration
files then environment variables, is always returned.

Installation
============

This package is stored in PyPI and can be installed the standard way::

    pip install crumbs

The latest release available is:

.. image:: https://badge.fury.io/py/crumbs.png
    :target: http://badge.fury.io/py/crumbs

Using Crumbs
============

Usage of this package is outlined in the documentation::

    pydoc crumbs

Developing Crumbs
=================

If you would prefer to clone this package directly from git or assist with 
development, the URL is https://github.com/alunduil/crumbs.

Crumbs is tested continuously by Travis-CI and running the tests is quite 
simple::

    flake8
    nosetests

The current status of the build is:

.. image:: https://secure.travis-ci.org/alunduil/crumbs.png?branch=master
   :target: http://travis-ci.org/alunduil/crumbs

Authors
=======

* Alex Brandt <alunduil@alunduil.com>
* Greg Switft <gregswift@gmail.com>

Known Issues
============

Known issues can be found in the github issue list at
https://github.com/alunduil/crumbs/issues.

Troubleshooting
===============

If you need to troubleshoot an issue or submit information in a bug report, we
recommend obtaining the following pieces of information:

* output with debug logging turned on in your application
* any relevant stack traces
