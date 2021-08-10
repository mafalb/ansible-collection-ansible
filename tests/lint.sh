#!/bin/bash -eu

# This file is part of Ansible Collection mafalb.ansible
# Copyright (c) 2021 Markus Falb <markus.falb@mafalb.at>
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

# run this script with
# $ bash tests/lint.sh
# or source it
# . tests/lint.sh
#

set -e

args=()

if test "$#" -gt 0
then

        if test "$1" == 'requirements'
        then
        	args[0]=--requirements
		shift
        fi
fi


if test "$#" -gt 0
then
        if test -n "$1"
        then
        	args+=(--python)
        	args+=("$1")
		shift
        fi
fi

echo "Checking for forgotten no_log..."
grep -qr "no_log: false\s*$" . && exit 1

echo "yamllint..."
yamllint -s .

echo "ansible-lint..."
ansible-lint -v

echo "ansible-lint of variables..."
ansible-lint -v roles/*/vars/*.yml

echo "flake8..."
flake8 -v

echo "ansible-test sanity..."
# shellcheck disable=SC2068
ansible-test sanity ${args[@]}
