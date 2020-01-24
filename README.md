# pylyskom

pylyskom is a Python library for communicating with LysKOM servers
over LysKOM Protocol A.

The source code for pylyskom can be found at:
https://github.com/osks/pylyskom

Packages are published in PyPI:
https://pypi.org/project/pylyskom/

LysKOM Protocol A specification can be found here:
https://www.lysator.liu.se/lyskom/protocol/


## Background

pylyskom was originally based on python-lyskom. The following files
originates from python-lyskom: kom.py, komauxitems.py, aux-items.txt
and make_komauxitems. Most of the changes since then comes from
httpkom's use of kom.py. Httpkom also built some wrappers (komsession)
around the kom.py code, to make it easier to use. Pylyskom was created
as an attempt to break out komsession and the modifications to kom.py
from httpkom.


## Code status

[![Build Status](https://travis-ci.org/osks/pylyskom.svg?branch=master)](https://travis-ci.org/osks/pylyskom)


## Development

### Preparing a release

On master:

1. Update and check CHANGELOG.md.
1. Increment version number and remove `+dev` suffix
   (in `pylyskom/version.py`).
1. Run tests locally with `make test`.
1. Commit, push.
1. Check CI build/test results. Also test manually by using jskom.
1. Tag (annotated) with `v<version>` (example: `v0.1`) and push the tag:
   ```
   git tag -a v0.1 -m "Version 0.1"
   git push origin v0.1
   ```
1. Build PyPI dist: `make dist`
1. Push to Test PyPI: `twine upload --repository testpypi dist/*` and check
   https://test.pypi.org/project/pylyskom/ .
1. Push to PyPI: `twine upload dist/*` and check
   https://pypi.org/project/pylyskom/ .
1. Add `+dev` suffix to version number, commit and push.


### Tools:

Twine is used for pushing the built dist to PyPI. The examples in the
release process depends on a `.pypirc` file with config for the pypi
and testpypi repositories.

Example of `.pypirc`:
```
[pypi]
username = __token__
password = pypi-...

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-...
```


## Copyright and license

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
