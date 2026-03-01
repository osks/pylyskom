pylyskom
========

pylyskom is a Python library for communicating with LysKOM servers
over LysKOM Protocol A.

The source code can be found at: https://github.com/osks/pylyskom

Packages are published on PyPI: https://pypi.org/project/pylyskom/

LysKOM Protocol A specification can be found here:
https://www.lysator.liu.se/lyskom/protocol/


Background
----------

pylyskom was originally based on python-lyskom. The following files
originates from python-lyskom: kom.py, komauxitems.py, aux-items.txt
and make_komauxitems. Most of the changes since then comes from
httpkom's use of kom.py. Httpkom also built some wrappers (komsession)
around the kom.py code, to make it easier to use. Pylyskom was created
as an attempt to break out komsession and the modifications to kom.py
from httpkom.


Development
-----------

Run tests locally::

    make test

Preparing a release
*******************

On master:

1. Update CHANGELOG.md.

2. Increment version number and remove ``+dev`` suffix
   (in ``pylyskom/version.py``).

3. Run tests locally with ``make test``.

4. Commit and push.

5. Create a GitHub release at https://github.com/osks/pylyskom/releases
   with tag ``v<version>`` (e.g. ``v0.9``). The release workflow will
   run tests and publish to PyPI automatically.

6. Bump version to next ``+dev`` suffix, commit and push.


Copyright and license
---------------------

Copyright (C) 2012-2026 Oskar Skoog

Copyright (C) 2008 Henrik Rindlöw

Copyright (C) 1999-2003 Kent Engström, Peter Liljenberg, Peter Åstrand,
Erik Forsberg, Ragnar Ouchterlony.

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
