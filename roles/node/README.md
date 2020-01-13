# Ansible Role - mafalb.ansible.node

Some ansible modules depends on external libraries. This Ansible role is meant to install them.

## Basic Usage

```yaml
- name: install node dependencies
  hosts: remote
  roles:
  - role: mafalb.ansible.node
```

## License

GPLv3
