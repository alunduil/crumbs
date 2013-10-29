Description
===========

Generalized all-in-one parameters module.

This package provides a single view of environment variables, configuration
files, and command line arguments.  The consistent interface makes interacting
with these, most of the time disparate, resources much simpler.  It also allows
parameters to be set on any of the three sources and the merge happens
automatically upon retrieval.  This way the most expected value is always used.

Installation
============

This package is stored in PyPI and can be installed the standard way::

    pip install crumbs

The latest release available is:

.. image:: https://badge.fury.io/py/crumbs.png
    :target: http://badge.fury.io/py/crumbs

If you would prefer to clone this package directly from git or assist with
development, the URL is https://github.com/alunduil/crumbs and the current
status of the build is:

.. image:: https://secure.travis-ci.org/alunduil/crumbs.png?branch=master
   :target: http://travis-ci.org/alunduil/crumbs

Usage
=====

Usage of this package is outlined in the module's documentation::

    pydoc crumbs

Authors
=======

* Alex Brandt <alunduil@alunduil.com>

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
