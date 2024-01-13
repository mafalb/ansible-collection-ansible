#!/usr/bin/python
# Copyright (c) Markus Falb
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# flake8: noqa: E501

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
module: virtualenv
author:
  - "Markus Falb (@mafalb)"
version_added: '6.0.0'
short_description: Create a virtualenv for ansible
notes: []
description:
  - Create a virtualenv for ansible
options:
  executable:
    description:
      - The C(python) binary with or without full C($PATH)
    required: false
    type: str
  name:
    description:
      - The pip packages to install.
    required: false
    default:
      - _ansible
    type: list
    elements: str
"""

EXAMPLES = r"""
- name: Install ansible into python 3.8 venv into ~/.virtualenvs/ansible
  mafalb.ansible.virtualenv:
    executable: python3.8
    path: ~/.virtualenvs/ansible

- name: Install ansible into ~/.virtualenvs/ansible
  mafalb.ansible.virtualenv:
    path: ~/.virtualenvs/ansible
    packages:
      - _ansible
      - molecule
      - ansible-lint
"""

RETURN = r"""
virtualenv:
    description:
      - TODO
    returned: always
    type: dict
    sample: '{
    }'
"""
