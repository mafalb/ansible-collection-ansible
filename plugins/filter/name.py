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


def filter_pipname_core(version):
    version = str(version)
    try:
        majorversion = int(version.split('.')[0])
        minorversion = int(version.split('.')[1])
        if majorversion == 2:
            if minorversion <= 9:
                return 'ansible'
            elif minorversion == 10:
                return 'ansible-base'
            else:
                return 'ansible-core'
        else:
            raise ValueError("I can not handle the ansible majorversion %s"
                             % version)
    except Exception as e:
        raise_from(AnsibleError('Error in filter_pipname_core, ',
                   'this was original exception: %s' % to_native(e)), e)


class FilterModule(object):
    def filters(self):
        return {
            'pipname_core': filter_pipname_core,
        }
