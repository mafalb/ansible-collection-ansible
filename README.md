# Ansible Collection - mafalb.ansible

||||
|---|---|---|
|master|![master branch CI](https://github.com/mafalb/ansible-collection-ansible/actions/workflows/CI.yml/badge.svg)|![master branch VERSIONCHECK](https://github.com/mafalb/ansible-collection-ansible/actions/workflows/VERSIONCHECK.yml/badge.svg)
|dev|![dev branch CI](https://github.com/mafalb/ansible-collection-ansible/actions/workflows/CI.yml/badge.svg?branch=dev)|![dev branch VERSIONCHECK](https://github.com/mafalb/ansible-collection-ansible/actions/workflows/VERSIONCHECK.yml/badge.svg?branch=dev)|

A collection for ansible related things.


## Plugins

### mafalb.ansible.virtualenv

### mafalb.ansible.python_info


## Roles

### [mafalb.ansible.controlnode](roles/controlnode/README.md)

Install ansible and dependencies on an ansible controlnode.

### [mafalb.ansible.node](roles/node/README.md)

Install dependencies on an ansible node.

### [mafalb.ansible.virtualenv](roles/virtualenv/README.md)

Install ansible and related tools into a virtualenv.
It uses constraints from ansible-test, e.g. dependencies installed locally doesn't interfere, use it

```shell
(venv) $ ansible-test sanity --local
(venv) $ ansible-test units --local
(venv) $ ansible-test integration --local
```

## License

Copyright (c) Markus Falb <markus.falb@mafalb.at>

GPL-3.0-or-later
