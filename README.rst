Description
-----------

Generalized all-in-one parameters module.

This package provides a single interface to environment variables,
configuration files, and command line arguments.  The dictionary-like interface
makes interacting with these disparate resources much simpler.  It also allows
parameters' values to be set in any of the three sources and selects an
appropriate value when a parameter's value is specified in multiple sources.
This way the most expected value, according to the normal prcedence—command
line arguments then configuration files then environment variables—is always
returned.

Getting Started
---------------

Usage of this package is outlined in the documentation_.

Reporting Issues
----------------

Any issues discovered should be recorded on Github_.  If you believe you've
found an error or have a suggestion for a new feature, please ensure that it is
reported.

If you would like to contribute a fix or new feature, please submit a pull
request.  This project follows `git flow`_ and utilizes travis_ to
automatically check pull requests before a manual review.

.. _documentation: https://crumbs.readthedocs.io/en/latest/
.. _git flow: http://nvie.com/posts/a-successful-git-branching-model/
.. _Github: https://github.com/alunduil/zfs-replicate
.. _travis: https://travis-ci.org/alunduil/crumbs
