# Copyright (c) 2021 Markus Falb <markus.falb@mafalb.at>
# GNU General Public License v3.0+
# see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt

from __future__ import (absolute_import, division, print_function)
from ansible.errors import AnsibleFilterError
from ansible_collections.mafalb.ansible.plugins.filter.ansible import (
    __fix_ansible_pip_req
)
__metaclass__ = type

import pytest

TEST_CASES = (
    ('ansible==2.11.6', 'ansible-core==2.11.6'),
    ('ansible~=2.10.0', 'ansible-base~=2.10.0'),
    ('ansible<2.9.99', 'ansible<2.9.99'),
)

FAIL_CASES = (
    ('ansible_test==2.11.6'),
    ('X==bla'),
    ([]),
    (2.10)
)


@pytest.mark.parametrize('req, expected', TEST_CASES)
def test_fix_ansible_pip_req(req, expected):
    actual = __fix_ansible_pip_req(req)
    assert actual == expected, "value was not {x} but {y}".format(
        x=expected, y=actual
    )


@pytest.mark.parametrize('req', FAIL_CASES)
def test_fail(req):
    try:
        x = __fix_ansible_pip_req(req)
    except (AnsibleFilterError):
        pass
    try:
        x
    except NameError:
        assert True
    else:
        assert False, "x exists and has value {value}".format(value=x)
