# Copyright (c) 2021 Markus Falb <markus.falb@mafalb.at>
# GNU General Public License v3.0+
# see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt

from __future__ import (absolute_import, division, print_function)
from ansible_collections.mafalb.ansible.plugins.module_utils.lib import (
    which
)
import pytest
__metaclass__ = type

FAIL_CASES_NONE = (
    ('idontexist-tkseikdgsngdfjpbdmtv'),
    ('/bin/idontexist-tkseikdgsngdfjpbdmtv'),
)

FAIL_CASES_EXCEPTION = (
    ({}),
    ([]),
    (2.10)
)


@pytest.mark.parametrize('exe', FAIL_CASES_NONE)
def test_which_is_None(exe):
    result = which(exe)
    assert result is None, "Result not None but {x}".format(x=result)


@pytest.mark.parametrize('exe', FAIL_CASES_EXCEPTION)
def test_which_raises(exe):
    with pytest.raises(TypeError):
        result = which(exe)  # noqa F841
