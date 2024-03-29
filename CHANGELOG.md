# Changelog for pylyskom

## Unreleased


## 0.8 (2022-09-12)

### Added

- Functionality for returning server info and changing / setting presentation.
- Functionality for setting password.

### Fixed

- Handle that supervisor in conf-stat can be 0.
- Handle AioKomsession being able to return texts by anonymous users,
  and comments to texts by anonymous users.


## 0.7 (2021-01-21)

### Fixed

- Handle that membership added-by can be 0.


## 0.6 (2021-01-20)

### Changed

- API changes to better handle returning conf-no and pers-no together
  with name, without anything else.

### Fixed

- Correctly handle conferences where the conferences for super conf,
  creator or supervisor return undefined conference.


## 0.5 (2020-07-03)

### Fixed

- Made get_current_person_no and is_logged_in in AioKomsession async methods.


## 0.4 (2020-07-01)

### Fixed

- Minor fixes


## 0.3 (2020-02-06)

### Added

- Asyncio support


## 0.2 (2020-01-22)

### Added

- Support for posting images (lyskom)
- Python 3 support
- Internal counters (stats / metrics)
- Use modern tools for Python (PyPI and tox)


## 0.1 (2016-05-29)

### Added

- First version.
- Added changelog.
