# Ansible Role - mafalb.ansible.node

Some ansible modules depends on external libraries. This Ansible role is meant to install them.

## Basic Usage

```yaml
- name: install node dependencies
  hosts: remote
  roles:
  - role: mafalb.ansible.node
    ansible_node_features:
    - crypto
    - selinux
```

## Variables

```ansible_node_features```

The following features are defined

* crypto - dependencies for crypto
* selinux - dependencies for selinux
* pip - dependencies for pip

## License

Copyright (c) 2020,2021 Markus Falb <markus.falb@mafalb.at>

GPL-3.0-or-later
