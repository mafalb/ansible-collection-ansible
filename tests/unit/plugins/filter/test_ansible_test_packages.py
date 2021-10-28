# Copyright (c) 2021 Markus Falb <markus.falb@mafalb.at>
# GNU General Public License v3.0+
# see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt

from __future__ import (absolute_import, division, print_function)
from ansible_collections.mafalb.ansible.plugins.filter.version import (
    __ansible_test_packages
)
from . data import data
__metaclass__ = type


def test_ansible_test_packages():
    p29 = __ansible_test_packages('2.9', data)
    p210 = __ansible_test_packages('2.10', data)
    p211 = __ansible_test_packages('2.11', data)

    assert isinstance(p29, list)
    assert isinstance(p210, list)
    assert isinstance(p211, list)

    assert len(p29) > 1
    assert len(p210) > 1
    assert len(p211) > 1

    assert sorted(p29) != sorted(p210)
    assert sorted(p29) != sorted(p211)
    assert sorted(p210) != sorted(p211)