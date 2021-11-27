# Copyright (c) 2021 Markus Falb <markus.falb@mafalb.at>
# GNU General Public License v3.0+
# see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt

from __future__ import (absolute_import, division, print_function)
from ansible.errors import AnsibleFilterError
from ansible_collections.mafalb.ansible.plugins.filter.ansible import (
    best_version
)
import pytest
__metaclass__ = type


TEST_CASES = (
    (['_ansible==2.12.0rc1'], '2.12.0rc1'),
    (['_ansible~=2.12.0'], '2.12.0'),
    (['_ansible==2.12'], '2.12.0'),
    (['_ansible==2.9'], '2.9.27'),
    (['_ansible==2.11.7'], '2.11.7'),
    (['_ansible==2.11.6'], '2.11.6'),
    (['_ansible==2.11.5'], '2.11.5'),
    (['_ansible<2.11.6'], '2.11.5'),
    (['_ansible~=2.9.6'], '2.9.27'),
    (['_ansible'], '2.12.0'),
    (['_ansible~=2.11.6', '_ansible_test'], '2.11.6'),
    (['ansible', '_ansible==2.11', '_ansible_test'], '2.11.6'),
)

T_WITH_PYTHON = (
    (['_ansible==2.12.0rc1'], '3.6', '2.12.0rc1'),
    (['_ansible~=2.12.0'], '3.8', '2.12.0'),
    (['_ansible==2.12'], '3.8', '2.12.0'),
    (['_ansible==2.9'], '3.8', '2.9.27'),
    (['_ansible==2.11.7'], '3.8', '2.11.7'),
    (['_ansible==2.11.6'], '3.8', '2.11.6'),
    (['_ansible==2.11.5'], '3.8', '2.11.5'),
    (['_ansible<2.11.6'], '3.5', '2.11.5'),
    (['_ansible~=2.9.6'], '3.8', '2.9.27'),
    (['_ansible'], '3.8', '2.12.0'),
    (['_ansible'], '3.7', '2.11.6'),
    (['_ansible~=2.11.6', '_ansible_test'], '3.8', '2.11.6'),
)

FAIL_CASES = (
    (['_ansible=="2.9"'], AnsibleFilterError),
    (['ansible=="2.9"'], AnsibleFilterError),
)


@pytest.mark.parametrize('in_list, expected', TEST_CASES)
def test_best_version(in_list, expected):
    actual = best_version(in_list)
    assert actual == expected, "got {actual} instead of {expected}".format(
        actual=actual, expected=expected
    )


@pytest.mark.parametrize('in_list, python_version, expected', T_WITH_PYTHON)
def test_best_version_with_python(in_list, python_version, expected):
    actual = best_version(in_list, python_version)
    assert actual == expected, "got {actual} instead of {expected}".format(
        actual=actual, expected=expected
    )


@pytest.mark.parametrize('version, exception', FAIL_CASES)
def test_fail(version, exception):
    with pytest.raises(exception):
        best_version(version)
