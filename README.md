# Ansible Collection - mafalb.ansible

A collection for ansible related things. Available roles:

## role: mafalb.ansible.molecule

Role for installing molecule. Molecule helps with testing ansible roles or collections. Use it local or with CI.

Molecule installs into a virtualenv without site packages, so there are minimal changes necessary on your system.

### Basic Usage

```ansible
- name: install molecule
  hosts: localhost
  roles:
    - role: mafalb.ansible.molecule
```

### Variables

```molecule_ansible_version: 2.8``` # set the ansible version you want to test against

```molecule_virtualenv: ~/.virtualenvs/testvenv``` # set the path to the virtualenv, default is ```~/.virtualenvs/molecule```

## License

GPLv3

