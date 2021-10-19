#!/bin/bash -eu

# Copyright (c) 2021 Markus Falb <markus.falb@mafalb.at>
# GNU General Public License v3.0+
# see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt

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
if test "$ANSIBLE_LINT_VERSION" == 4
then
	ansible-lint -v -c .ansible-lint-4
else
	ansible-lint -v
fi

echo "ansible-lint of variables..."
ansible-lint -v roles/*/vars/*.yml

echo "flake8..."
flake8 -v --exclude tests/output

echo "ansible-test sanity..."
# shellcheck disable=SC2068
ansible-test sanity ${args[@]}
