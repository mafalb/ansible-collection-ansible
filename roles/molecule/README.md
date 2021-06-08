# Ansible Role - mafalb.ansible.molecule

A Role for installing Molecule. Molecule helps with testing ansible roles or collections. Use it local or with CI.

Molecule installs via pip into a virtualenv without site packages.

molecule version 3.3.0 introduced a dependency for ansible-lint 5 which for me gave me incompatibilities. Therefore I bumped the major version of this collection.

mafalb.ansible up to 2.1.1 -> ansible-lint <5
mafalb.ansible > 3.0.0 -> ansible-lint >5

## Basic Usage

```yaml
- name: install molecule
  hosts: localhost
  roles:
  - role: mafalb.ansible.molecule
```

## Variables

Variables are optional. Only specify them if you want to override the defaults.

```molecule_version``` To pin to a specific version.

```yaml
molecule_version: 3
```

```yaml
molecule_version: 3.1
```

```molecule_update``` Set if you want to update an existent installation of molecule

```yaml
molecule_update: true
```

```molecule_ansible_version``` set the ansible version you want to test against

this is the version of the ansible-core (or ansible-base) package, not the version of the ansible package

```yaml
molecule_ansible_version: 2.11
```

```molecule_ansible_community_version``` the version of ansible community, i.e. the ansible package

```yaml
molecule_ansible_community_version: 4.0.0
```

```molecule_virtualenv``` set the path to the virtualenv. Specify a absolute path. ```~/something``` will not work.

```yaml
molecule_virtualenv: "{{ ansible_user_dir }}/.virtualenvs/testvenv
```

```molecule_enablerepo``` enable additional package repositories

```yaml
molecule_enablerepo: cr
```

## License

Copyright (c) 2020,2021 Markus Falb <markus.falb@mafalb.at>

GPL-3.0-or-later
