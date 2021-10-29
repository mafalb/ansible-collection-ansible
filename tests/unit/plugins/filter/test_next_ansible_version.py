# Copyright (c) 2021 Markus Falb <markus.falb@mafalb.at>
# GNU General Public License v3.0+
# see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt

from __future__ import (absolute_import, division, print_function)
from ansible.errors import AnsibleFilterError
from ansible_collections.mafalb.ansible.plugins.filter.ansible import (
    next_ansible_version
)
__metaclass__ = type

import pytest

TEST_CASES = (
    ('2.11'),
    ('2.10'),
    ('2.9'),
)

FAIL_CASES = (
    ('2.11.'),
    ('2.'),
    ('2'),
    ('2.11.7.7'),
    ([]),
    (2),
)


@pytest.mark.parametrize('version', TEST_CASES)
def test_next_ansible_version(version):
    actual = next_ansible_version(version)
    assert actual.startswith(version), "does not start with {x}".format(
        x=version
    )


@pytest.mark.parametrize('version', FAIL_CASES)
def test_version2int_special_cases(version):
    with pytest.raises(AnsibleFilterError):
        next_ansible_version(version)
