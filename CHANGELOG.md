# Changelog

## v0.2.2 XXXX-XX-XX

### Changes

- _ansibles_version was referenced although it might not be set

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
