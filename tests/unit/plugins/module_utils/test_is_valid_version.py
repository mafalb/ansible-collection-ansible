# Copyright (c) 2021 Markus Falb <markus.falb@mafalb.at>
# GNU General Public License v3.0+
# see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt

from __future__ import (absolute_import, division, print_function)
from ansible_collections.mafalb.ansible.plugins.module_utils.python import (
    is_valid_version
)
import pytest
__metaclass__ = type

TEST_CASES = (
    ('Python 3.10.0', True),
    ('Python 3.6.8', True),
    ('Python 2.7.2', True),
    ('Python 4.0.1', False),
    ('3.6.8', False),
    ('Python 3.bla.0', False),
    (3, False),
    ({}, False),
    ([], False),
    (2.10, False)
)


@pytest.mark.parametrize('version, expected', TEST_CASES)
def test_is_valid_version(version, expected):
    result = is_valid_version(version)
    assert expected == result, "Result not {x} but {y}".format(
                                                            x=expected,
                                                            y=result
                                                            )
