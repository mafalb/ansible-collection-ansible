# Copyright (c) Markus Falb <markus.falb@mafalb.at>
# GNU General Public License v3.0+
# see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt

from __future__ import absolute_import, division, print_function
__metaclass__ = type


def is_valid_version(version):
    """Check if it is a valid python version"""
    try:
        if not version.startswith("Python "):
            return False
    except AttributeError:
        return False
    version = version.split()[1]
    if not len(version.split('.')) == 3:
        return False
    if not version[0] in ['2', '3']:
        return False
    try:
        if not isinstance(int(version.split('.')[1]), int):
            return False
    except ValueError:
        return False
    return True
