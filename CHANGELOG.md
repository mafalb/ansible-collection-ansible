# Changelog

## v2.1.0 XXXX-XX-XX

- added role for controlnode
- added role for ansible-lint
- CI Tests for CentOS Stream 8

## v2.0.1 2021-02-14

- just internal work for CI, induced by new cryptographys dependency on rust

## v2.0.0 2021-01-24

- relicense to GPL-3.0-or-later
- use jinja2 < 2.11 to catch errors with missing true test. this could cause incompatibilities.

## v1.0.0 2021-01-16

- remove the scripts for role and collection creation, use cookiecutters-ansible [1] project instead
- CI: install pylint and rstcheck, make ansible-test happy
- relicense to BSD-3-Clause

[1] [https://github.com/mafalb/cookiecutters-ansible](https://github.com/mafalb/cookiecutters-ansible)

## v0.3.3 2020-12-20

- revert pin of rich
- revert pin of chardet
- improvements to CI

## v0.3.2 2020-12-19

- pin rich<9.5.0, fix for [issue 3](https://github.com/mafalb/ansible-collection-ansible/issues/3)

## v0.3.1 2020-12-11

- force chardet <0.3.1 for molecule installs
- better CI efficiency (get ansible version out of molecules version)

## v0.3.0 2020-12-07

### Changes

- molecule and ansible are installed in one single task
- remove molecule_update_ansible variable
- _ansibles_version was referenced although it might not be set
- default to latest version of molecule
- rename molecule_major_version to molecule_version.
- make updating work

### Changes to CI

- do not set ANSIBLE_COLLECTIONS_PATH
- refactored tests
- test molecule_update and molecule_update_ansible

## v0.2.1 2020-11-26

### Changes

- improvements to collection_skeleton
- default to molecule version 3.1, not the latest, there are some problems with 3.2

## v0.2.0 2020-11-06

### Changes

- remove support for molecule 2
- added variables for updating molecule and ansible

### Changes to CI

- test on Fedora 33

## v0.1.3 2010-10-17

### Changes to CI

- check ansible versions
- colored output for molecule runs
- fix check for molecule version

## v0.1.2 2020-10-10

### Changes

- use ansible 2.10 by default

### Changes to CI

- use actions/checkout@v2
- use default working-dir
- do not pin molecule version to 3.0.4 anymore


## v0.1.1 2020-08-22

### Added

- molecule: install testinfra along with molecule
- CHANGELOG

### Changed

- a lot of changes and bug fixes to CI

### Removed

- drop support for fedora 30 (EOL)
