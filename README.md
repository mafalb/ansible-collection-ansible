# Ansible Collection - mafalb.ansible

A collection for ansible related things.

## role: mafalb.ansible.molecule

Role for installing Molecule. Molecule helps with testing ansible roles or collections. Use it local or with CI.

Molecule installs via pip into a virtualenv without site packages.

### Basic Usage

```ansible
- name: install molecule
  hosts: localhost
  roles:
  - role: mafalb.ansible.molecule
```

### Variables

All these variables are optional. Only specify them if you want to override the defaults.

```molecule_major_version: 2``` # the molecule major version

```molecule_ansible_version: 2.9``` # the ansible version you want to test against

```molecule_virtualenv: "{{ ansible_user_dir }}/.virtualenvs/testvenv``` # the path to the virtualenv

## License

GPLv3

