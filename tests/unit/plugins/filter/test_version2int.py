# Copyright (c) 2021 Markus Falb <markus.falb@mafalb.at>
# GNU General Public License v3.0+
# see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt

from __future__ import (absolute_import, division, print_function)
from ansible.errors import AnsibleFilterError
from ansible_collections.mafalb.ansible.plugins.filter.ansible import (
    version2int
)
__metaclass__ = type

import pytest

VERSION2INT_TEST_CASES = (
    ('2.11.6', 21106),
    ('2.11.0', 21100),
    ('2.10.99', 21099),
    # sorted wrong because of overflow
    # we hope that release numbering never gets that far
    ('2.10.100', 21100),
    ('2.10.0', 21000),
    ('2.9.10', 20910),
    ('2.12.0rc1', 0),
    ('2.12.0b2', 0),
    ('2.12', 21200),
)

VERSION2INT_SPECIAL_CASES = (
    ('notnumeric'),
    (''),
)


@pytest.mark.parametrize('version, expected', VERSION2INT_TEST_CASES)
def test_version2int(version, expected):
    actual = version2int(version)
    assert actual == expected, "value was not {x} but {y}".format(
        x=expected, y=actual
    )


def test_version2int_relative():
    assert version2int('2.9.10') < version2int('2.10.0')
    assert version2int('2.9.99') < version2int('2.10.0')


@pytest.mark.parametrize('version', VERSION2INT_SPECIAL_CASES)
def test_version2int_special_cases(version):
    try:
        x = version2int(version)
    except (AnsibleFilterError):
        pass
    try:
        x
    except NameError:
        assert True
    else:
        assert False, "x exists and has value {value}".format(value=x)
