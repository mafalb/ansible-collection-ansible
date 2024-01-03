# Copyright (c) 2021 Markus Falb <markus.falb@mafalb.at>
# GNU General Public License v3.0+
# see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt

from __future__ import (absolute_import, division, print_function)
from ansible_collections.mafalb.ansible.plugins.filter.ansible import (
    __ansible_test_packages
)

import yaml

datafile = open('roles/virtualenv/vars/data.yml', 'r')
data = yaml.load(datafile, Loader=yaml.Loader)
datafile.close()


__metaclass__ = type


def test_data_integrity():
    for ansible_version in data['python_versions']:
        data['ansible_test_packages'][ansible_version]
    for ansible_version in data['python_versions']:
        data['latest_version'][ansible_version]
    for ansible_version in data['latest_version']:
        data['ansible_test_packages'][ansible_version]


def test_ansible_test_packages():
    p29 = __ansible_test_packages('2.9')
    p210 = __ansible_test_packages('2.10')
    p211 = __ansible_test_packages('2.11')
    p212 = __ansible_test_packages('2.12')

    assert isinstance(p29, list)
    assert isinstance(p210, list)
    assert isinstance(p211, list)
    assert isinstance(p212, list)

    assert len(p29) > 1
    assert len(p210) > 1
    assert len(p211) > 1
    assert len(p212) > 1

    assert sorted(p29) != sorted(p210)
    assert sorted(p29) != sorted(p211)
    assert sorted(p210) != sorted(p211)
    assert sorted(p211) != sorted(p212)
