# Ansible Collection - mafalb.ansible

|||
|---|---|
|master|![master branch](https://github.com/mafalb/ansible-collection-ansible/workflows/CI/badge.svg)|
|dev|![dev branch](https://github.com/mafalb/ansible-collection-ansible/workflows/CI/badge.svg?branch=dev)|

A collection for ansible related things.

We recommend to set [INTERPRETER_PYTHON](https://docs.ansible.com/ansible/latest/reference_appendices/config.html#interpreter-python) to auto to avoid confusion between python 2 and 3.

For reference here is the link to the source code for INTERPRETER_PYTHON_DISTRO_MAP [lib/ansible/config/base.yml](https://raw.githubusercontent.com/ansible/ansible/devel/lib/ansible/config/base.yml)

## Roles

### [mafalb.ansible.controlnode](roles/controlnode/README.md)

### [mafalb.ansible.lint](roles/lint/README.md)

### [mafalb.ansible.molecule](roles/molecule/README.md)

### [mafalb.ansible.node](roles/node/README.md)

### [mafalb.ansible.virtualenv](roles/virtualenv/README.md)

## License

Copyright (c) 2020,2021 Markus Falb <markus.falb@mafalb.at>

GPL-3.0-or-later
