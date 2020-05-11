# Ansible Role - mafalb.ansible.molecule

A Role for installing Molecule. Molecule helps with testing ansible roles or collections. Use it local or with CI.

Molecule installs via pip into a virtualenv without site packages.

## Basic Usage

```yaml
- name: install molecule
  hosts: localhost
  roles:
  - role: mafalb.ansible.molecule
```

```yaml
- name: install version 2 of molecule
  hosts: localhost
  roles:
  - role: mafalb.ansible.molecule
    molecule_major_version: 2
    molecule_virtualenv: "~/.virtualenvs/molecule2"
```

## Variables

Variables are optional. Only specify them if you want to override the defaults.

```molecule_major_version``` There should be no need to specify this.

```yaml
molecule_major_version: 3
```

```molecule_ansible_version``` set the ansible version you want to test against

```yaml
molecule_ansible_version: 2.9
```

```molecule_virtualenv``` set the path to the virtualenv. Specify a absolute path. ```~/something``` will not work.

```yaml
molecule_virtualenv: "{{ ansible_user_dir }}/.virtualenvs/testvenv
```

## License

GPLv3
