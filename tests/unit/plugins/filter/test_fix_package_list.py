# Copyright (c) 2021 Markus Falb <markus.falb@mafalb.at>
# GNU General Public License v3.0+
# see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt

from __future__ import (absolute_import, division, print_function)
from ansible_collections.mafalb.ansible.plugins.filter.ansible import (
    pip_package_list
)
__metaclass__ = type

import pytest

TEST_CASES = (
    (['_ansible==2.12.0rc1'], ['ansible-core==2.12.0rc1']),
    (['_ansible==2.12.0rc1', '_ansible_test'], ['ansible-core==2.12.0rc1']),
    (['_ansible==2.11'], ['ansible-core==2.11.6']),
    (['_ansible==2.11.6'], ['ansible-core==2.11.6']),
    (['_ansible<2.11.6'], ['ansible-core<2.11.6']),
    (['_ansible~=2.9.6'], ['ansible~=2.9.6']),
    (['_ansible'], ['ansible-core']),
    (['_ansible~=2.11.6', '_ansible_test'],
     ['ansible-core~=2.11.6', 'voluptuous']),
)


@pytest.mark.parametrize('in_list, out_list', TEST_CASES)
def test_fix_package_list(in_list, out_list):
    actual = pip_package_list(in_list)
    for req in out_list:
        assert req in actual, "'{req}' is not in '{res}'".format(req=req,
                                                                 res=actual)
