#!/usr/bin/python
# Copyright (c) Markus Falb
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# flake8: noqa: E501

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
module: python_info
author:
  - "Markus Falb (@mafalb)"
version_added: '5.0.0'
short_description: Get info about a python interpreter
notes: []
description:
  - Get info about a python interpreter.
options:
  executable:
    description:
      - Path to C(buildah) executable if it is not in the C($PATH) on the
        machine running C(buildah)
    required: true
    type: str
"""

EXAMPLES = r"""
- name: Get info about python3.8 by absolute path
  mafalb.containers.python_info:
    executable: /usr/bin/python3.8
  register: python

- name: Get info about python3.8 by relative path
  mafalb.containers.python_info:
    executable: python3.8
  register: python
"""

RETURN = r"""
python_info:
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
        "actions": [
            "recreated container"
        ],
        "buildah_actions": [
            "buildah rm container",
            "buildah --name container --cap-drop CAP_SYS_ADMIN from hello-world"
        ],
        "changed": false,
        "version": {
           "major": "3",
           "minor": "8",
           "majmin": "3.8",
        },
        "path": "/usr/bin/python3.8",
        "failed": false,
    }'
"""

from ansible.module_utils.basic import AnsibleModule  # noqa: E402
from ansible_collections.mafalb.ansible.plugins.module_utils.python import is_valid_version  # noqa: E402
from ansible_collections.mafalb.ansible.plugins.module_utils.lib import which  # noqa: E402
import os


def main():
    module_args = dict(
        executable=dict(type='str', required=True),
    )
    results = dict(
        changed=False,
        failed=True,
        version={},
    )
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    if not module.params['executable']:
        module.fail_json(msg="which executable?")

    executable = module.params['executable']

    if not executable.startswith(os.pathsep):
        executable = which(executable)

    # run python --version
    rc, out, err = module.run_command([executable, '--version'])

    if rc != 0:
        module.fail_json(msg="Failed getting version for {x}.".format(x=executable))
    if err.startswith("Python "):
        # older python dump version on stderr
        out = err
    if not is_valid_version(out):
        module.fail_json(msg="Not a valid version {v}.".format(v=out))

    # "Python 3.6.8"
    version = out.split()[1]

    results['version']['major'] = int(version[0])
    results['version']['minor'] = int(version.split('.')[1])
    results['version']['majmin'] = '.'.join(version.split('.')[0:2])
    results['executable'] = executable
    results['failed'] = False

    module.exit_json(**results)


if __name__ == '__main__':
    main()
