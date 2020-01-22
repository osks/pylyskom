
pylyskom
========

pylyskom is a Python library for talking with LysKOM servers.

pylyskom was originally based on python-lyskom. The following files
originates from python-lyskom: kom.py, komauxitems.py, aux-items.txt
and make_komauxitems. Most of the changes since then comes from
httpkom's use of kom.py. Httpkom also built some wrappers (komsession)
around the kom.py code, to make it easier to use. Pylyskom was created
as an attempt to break out komsession and the modifications to kom.py
from httpkom.

The source code for pylyskom can be found at:
https://github.com/osks/pylyskom


Dependencies
------------

For required Python packages, see requirements.txt. Install them with:

    $ pip install -r requirements.txt


Code status
-----------

[![Build Status](https://travis-ci.org/osks/pylyskom.svg?branch=master)](https://travis-ci.org/osks/pylyskom)


Copyright and license
---------------------

Copyright (C) 2012-2020 Oskar Skoog

Copyright (C) 2008 Henrik Rindlöw

Copyright (C) 1999-2003 Kent Engström, Peter Liljenberg, 
                        Peter Åstrand, Erik Forsberg,
                        Ragnar Ouchterlony.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
MA  02110-1301, USA.
