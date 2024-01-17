# Copyright (c) Markus Falb <markus.falb@mafalb.at>
# GNU General Public License v3.0+
# see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt

from __future__ import (absolute_import, division, print_function)
from packaging.specifiers import SpecifierSet
from ansible_collections.mafalb.ansible.plugins.filter.ansible import (
    __gen_old_ansible_versions,
    __gen_new_ansible_versions,
    __is_old_ansible,
)
__metaclass__ = type

import pytest
import yaml

datafile = open('roles/virtualenv/vars/data.yml', 'r')
data = yaml.load(datafile, Loader=yaml.Loader)
datafile.close()


TEST_OLD_ANSIBLE_VERSION = (
    ('~=2.9.27', True),
    ('<=2.10.7', True),
    ('>2.10.7', False),
    ('<2.10', True),
    ('<=2.10.8', False),
    ('==2.11.8', False),
    ('~=2.16.0', False),
    ('', False),
)


def test_gen_old_ansible_versions():
    versions = __gen_old_ansible_versions()
    assert '2.9.27' in versions
    assert '2.10.7' in versions
    assert '2.10.8' not in versions


def test_gen_new_ansible_versions():
    versions = __gen_new_ansible_versions()
    assert '2.9.27' not in versions
    assert '2.10.7' not in versions
    assert '2.10.8' in versions
    assert '2.11.2' in versions
    assert '2.16.2' in versions


@pytest.mark.parametrize('version, expected', TEST_OLD_ANSIBLE_VERSION)
def test_is_old_ansible(version, expected):
    actual = __is_old_ansible(SpecifierSet(version))
    assert actual == expected, "value was not {x} but {y}".format(x=expected, y=actual)
