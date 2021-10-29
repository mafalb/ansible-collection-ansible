# Copyright (c) 2021 Markus Falb <markus.falb@mafalb.at>
# GNU General Public License v3.0+
# see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt

from __future__ import (absolute_import, division, print_function)
from ansible.errors import AnsibleFilterError, AnsibleFilterTypeError
from ansible_collections.mafalb.ansible.plugins.filter.ansible import (
    __major_minor_version
)
__metaclass__ = type

import pytest

TEST_CASES = (
    ('_ansible==2.12.0rc1', '2.12'),
    ('_ansible==2.11.6', '2.11'),
    ('_ansible~=2.10.0', '2.10'),
    ('_ansible<2.9.99', '2.9'),
    ('_ansible>2.10.9', '2.11'),
)

INVALID_CASES = (
)

FAIL_CASES = (
    ('_ansible>=2.12.0.rc1'),
    ('2'),
    ('2.'),
    (''),
    ('notnumeric'),
    ([]),
    (2.10)
)


@pytest.mark.parametrize('req, expected', TEST_CASES)
def test_major_minor_version(req, expected):
    actual = __major_minor_version(req)
    assert actual == expected, "value was not {x} but {y}".format(
        x=expected, y=actual
    )


@pytest.mark.parametrize('req', FAIL_CASES)
def test_fail(req):
    try:
        x = __major_minor_version(req)
    except (AnsibleFilterTypeError, AnsibleFilterError):
        pass
    try:
        x
    except NameError:
        assert True
    else:
        assert False, "x exists and has value {value}".format(value=x)
