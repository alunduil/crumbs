# Copyright (C) 2013 by Alex Brandt <alunduil@alunduil.com>
#
# pmort is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

class Parameters(object):
    def __init__(self):
        '''Initialize Parameters with the given items.

        This initializes a blank set of parameters to which parameters and
        configuration files may be added.

        This object keeps track of multiple configuration files and multiple
        groupings of parameters.

        '''

        self.defaults = {}
        self.parameters = {}
        self.configuration_files = {}
        self.groups = { 'default': {} }
        self.parsed = False
