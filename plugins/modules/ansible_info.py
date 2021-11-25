#!/usr/bin/python
# Copyright (c) 2020 RedHat, 2021 Markus Falb
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# flake8: noqa: E501

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
module: ansible_info
author:
  - "Markus Falb (@mafalb)"
version_added: '5.0.0'
short_description: Get info about an ansible
notes: []
description:
  - Get info about an ansible interpreter.
options:
  executable:
    description:
      - Path to ansible C(executable)
    default: ansible
    type: str
"""

EXAMPLES = r"""
- name: Get info about ansible
  mafalb.containers.ansible_info:
    executable: ~/.virtualenvs/ansible/bin/ansible
  register: ansible
"""

RETURN = r"""
ansible_info:
    description:
      - Facts representing the current state of the container. Matches the
        buildah inspect output.
      - Note that facts are part of the registered vars since Ansible 2.8. For
        compatibility reasons, the facts
        are also accessible directly as C(buildah_container). Note that the
        returned fact will be removed in Ansible 2.12.
      - Empty if C(state) is I(absent).
    returned: always
    type: dict
    sample: '{
        "changed": false,
        "version": {
           "full": "2.11.6"
           "major": "2",
           "minor": "11",
           "majmin": "2.11",
        },
        "path": "/home/bla/.virtualenvs/ansible/bin/ansible",
        "failed": false,
    }'
"""

from ansible.module_utils.basic import AnsibleModule  # noqa: E402
from ansible_collections.mafalb.ansible.plugins.module_utils.python import is_valid_version  # noqa: E402
from ansible_collections.mafalb.ansible.plugins.module_utils.lib import which  # noqa: E402
import os
import re


def main():
    module_args = dict(
        executable=dict(type='str', default='ansible'),
    )
    results = dict(
        changed=False,
    )
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    executable = module.params['executable']
    if not executable.startswith(os.pathsep):
        executable = which(executable)

    # run ansible --version
    rc, out, err = module.run_command([executable, '--version'])
    if rc != 0:
        module.fail_json(msg="Failed getting version for {x}.".format(x=executable))

    regex = re.compile(r'(\d+)\.(\d+)\.(\d+)')
    match = regex.search(out.splitlines()[0])
    if not match:
        module.fail_json(msg="Not a valid version for {x}.".format(x=out.splitlines()[0]))

    results['version']['major'] = int(match.group(1))
    results['version']['minor'] = int(match.group(2))
    results['version']['revision'] = int(match.group(3))
    results['version']['majmin'] = '.'.join([match.group(1), match.group(2)])
    results['version']['full'] = match.group(3)
    results['executable'] = executable

    module.exit_json(**results)


if __name__ == '__main__':
    main()
