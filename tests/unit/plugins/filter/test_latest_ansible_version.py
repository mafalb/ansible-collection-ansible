# Copyright (c) 2021 Markus Falb <markus.falb@mafalb.at>
# GNU General Public License v3.0+
# see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt

from __future__ import (absolute_import, division, print_function)
from ansible.errors import AnsibleFilterError, AnsibleFilterTypeError
from ansible_collections.mafalb.ansible.plugins.filter.version import latest_ansible_version
__metaclass__ = type

import pytest

TEST_CASES = (
    (['_ansible==2.11.6'], '2.11.6'),
    (['_ansible<2.11.6'], '2.11.5'),
    (['_ansible~=2.9.6'], '2.9.27'),
    (['_ansible'], '2.11.6'),
    (['_ansible~=2.11.6', '_ansible_test'], '2.11.6'),
)


@pytest.mark.parametrize('in_list, expected', TEST_CASES)
def test_fix_package_list(in_list, expected):
    actual = latest_ansible_version(in_list)
    assert actual == expected, "got {actual} instead of {expected}".format(actual=actual, expected=expected)
