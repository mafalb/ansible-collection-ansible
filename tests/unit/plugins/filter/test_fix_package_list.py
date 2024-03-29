# Copyright (c) Markus Falb <markus.falb@mafalb.at>
# GNU General Public License v3.0+
# see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt

from __future__ import (absolute_import, division, print_function)
from ansible_collections.mafalb.ansible.plugins.filter.ansible import (
    pip_package_list,
    __version2int,
)
__metaclass__ = type

import pytest
import yaml

datafile = open('roles/virtualenv/vars/data.yml', 'r')
data = yaml.load(datafile, Loader=yaml.Loader)
datafile.close()

latest = sorted(data['latest_ansible_version'], key=__version2int)[-1]

TEST_CASES = (
    (['_ansible'], ['ansible-core']),
)

# all tests with version numbers are prone to fail sometimes
# eventually the installed python is too new for the ansible
#
TEST_CASES_WITH_PYTHON = (
    (['_ansible==2.12.0rc1'], '3.8', ['ansible-core==2.12.0rc1']),
    (['_ansible==2.12.0rc1', '_ansible_test'], '3.8',
     ['ansible-core==2.12.0rc1']),
    (['_ansible==2.11'], '3.8',
     ['ansible-core==' + data['latest_ansible_version']['2.11']]),
    (['_ansible==2.11'], None,
     ['ansible-core==' + data['latest_ansible_version']['2.11']]),
    (['_ansible==2.11.6'], '3.8', ['ansible-core==2.11.6']),
    (['_ansible<2.11.6'], '3.8', ['ansible-core<2.11.6']),
    (['_ansible~=2.9.6'], '3.8', ['ansible~=2.9.6']),
    (['_ansible'], '3.6', ['ansible-core']),
    (['_ansible~=2.11.6', '_ansible_test'], '3.8',
     ['ansible-core~=2.11.6', 'voluptuous']),
    (["_ansible~=2.14.3", "ansible-lint", "molecule"], '3.9',
     ["ansible-core~=2.14.3", "ansible-lint", "molecule"]),
    (["_ansible_test", "_ansible~=2.14.3", "ansible-lint", "molecule"], '3.9',
     ["ansible-core~=2.14.3", "ansible-lint", "molecule"]),
    (["_ansible==2.9", "molecule~=3.3.0", "ansible-lint", "_ansible_test"],
     '3.8', ['ansible==2.9.27', 'voluptuous']),
)


@pytest.mark.parametrize('in_list, out_list', TEST_CASES)
def test_fix_package_list(in_list, out_list):
    actual = pip_package_list(in_list)
    for req in out_list:
        assert req in actual, "'{req}' is not in '{res}'".format(req=req,
                                                                 res=actual)


@pytest.mark.parametrize(
    'in_list, python_version, out_list',
    TEST_CASES_WITH_PYTHON
)
def test_fix_package_list_with_python(in_list, python_version, out_list):
    actual = pip_package_list(in_list, python_version)
    for req in out_list:
        assert req in actual, "'{req}' is not in '{res}'".format(req=req,
                                                                 res=actual)
