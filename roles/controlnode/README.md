# Ansible Role - mafalb.ansible.controlnode

A Role for installing ansible.
It's currently tested on

- CentOS 7
- CentOS 8
- CentOS Stream
- Fedora 32
- Fedora 33
- Ubuntu 20.04 (focal)

## Basic Usage

```yaml
- name: install ansible
  hosts: localhost
  roles:
  - role: mafalb.ansible.controlnode
```

## License

Copyright (c) 2020,2021 Markus Falb <markus.falb@mafalb.at>

GPL-3.0-or-later
