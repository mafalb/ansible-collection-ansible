# Copyright (c) Markus Falb <markus.falb@mafalb.at>
# GNU General Public License v3.0+
# see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt

from __future__ import (absolute_import, division, print_function)
from ansible.errors import AnsibleFilterError
from ansible_collections.mafalb.ansible.plugins.filter.ansible import (
    __detect_ansible_package,
)
__metaclass__ = type

import pytest
import yaml

datafile = open('roles/virtualenv/vars/data.yml', 'r')
data = yaml.load(datafile, Loader=yaml.Loader)
datafile.close()

# False if an exception is expected, this is a collision
# True if the list is OK
#
TEST_CASES = (
    (['ansible-core', 'ansible-base'], False),
    (['ansible-core', 'ansible==2.9.27'], False),
    (['ansible-core', 'ansible<2.10.8'], False),
    (['ansible-core', 'ansible<2.10'], False),
    (['ansible-core', 'ansible>2.10.7'], True),
    (['ansible<2.10', 'ansible>2.10.7'], True),  # what to do?
    (['ansible'], True),  # assume new style ansible
)


@pytest.mark.parametrize('package_list, expected', TEST_CASES)
def test_detect_collision(package_list, expected):
    try:
        actual = __detect_ansible_package(package_list)
    except (AnsibleFilterError):
        assert not expected, "This test was not expected to fail {t}".format(t=package_list)
    else:
        assert expected, "value was not {x} but {y}".format(x=expected, y=actual)
