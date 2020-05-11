# Ansible Role - mafalb.ansible.node

Some ansible modules depends on external libraries. This Ansible role is meant to install them.

## Basic Usage

```yaml
- name: install node dependencies
  hosts: remote
  roles:
  - role: mafalb.ansible.node
    ansible_node_features:
    - tls
    - selinux
```

## Variables

```ansible_node_features```

The following features are defined

* tls - dependencies for crypto
* selinux - dependencies for selinux
* pip - dependencies for pip

## License

GPLv3
