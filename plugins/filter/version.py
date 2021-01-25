# vim: set ts=4 expandtab:

# This file is part of Ansible Collection mafalb.ansible
# Copyright (c) 2020-2021 Markus Falb <markus.falb@mafalb.at>
#
# Ansible collection mafalb.ansible is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Ansible collection mafalb.ansible is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible collection mafalb.ansible.
# If not, see <https://www.gnu.org/licenses/>.

from __future__ import (absolute_import, division, print_function)
from ansible.module_utils.six import raise_from
from ansible.errors import AnsibleError
from ansible.module_utils._text import to_native
__metaclass__ = type


def filter_pipver(version):
    version = str(version)
    try:
        if (version.count('.') == 2):
            return version
        elif (version.count('.') == 1):
            return version + ".*"
        elif (version.count('.') == 0):
            return version + ".*"
        else:
            raise AnsibleError('Bad version number: %s' % version)
    except Exception as e:
        raise_from(AnsibleError('Error in filter_pipver, ',
                   'this was original exception: %s' % to_native(e)), e)


def filter_semver(version):
    version = str(version)
    try:
        if (version.count('.') == 2):
            return version.replace('*', '0')
        elif (version.count('.') == 1):
            return (version + ".0").replace('*', '0')
        elif (version.count('.') == 0):
            return (version + ".0.0").replace('*', '0')
        else:
            raise AnsibleError('Wrong version number: %s' % version)
    except Exception as e:
        raise_from(AnsibleError('Error in filter_semver, ',
                   'this was original exception: %s' % to_native(e)), e)


class FilterModule(object):
    def filters(self):
        return {
            'pipver': filter_pipver,
            'semver': filter_semver,
        }
