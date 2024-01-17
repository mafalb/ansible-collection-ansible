# Copyright (c) Markus Falb <markus.falb@mafalb.at>
# GNU General Public License v3.0+
# see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt

from __future__ import (absolute_import, division, print_function)
from ansible.errors import AnsibleFilterError
from ansible_collections.mafalb.ansible.plugins.filter.ansible import (
    __majmin
)
__metaclass__ = type

import pytest

TEST_CASES = (
    ('2.16', '2.16'),
    ('2.12.0rc1', '2.12'),
    ('2.12.0', '2.12'),
    ('2.11.6', '2.11'),
    ('2.10.0', '2.10'),
    ('2.9.99', '2.9'),
    ('2.10.9', '2.10'),
)

FAIL_CASES = (
    ('2'),
    ('2.'),
    (''),
    ('notnumeric'),
    ([]),
    (2.10)
)


@pytest.mark.parametrize('version, expected', TEST_CASES)
def test_major_minor_version(version, expected):
    actual = __majmin(version)
    assert actual == expected, "value was not {x} but {y}".format(x=expected, y=actual)


@pytest.mark.parametrize('version', FAIL_CASES)
def test_fail(version):
    try:
        x = __majmin(version)
    except (AnsibleFilterError):
        pass
    try:
        x
    except NameError:
        assert True
    else:
        assert False, "x exists and has value {value}".format(value=x)
