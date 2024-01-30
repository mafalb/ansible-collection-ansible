#!/bin/bash -eu

# Copyright (c) Markus Falb <markus.falb@mafalb.at>
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

ls -l .ansible-lint*

ANSIBLE_LINT_VERSION=$(NO_COLOR=1 ansible-lint --version | awk '/^ansible-lint / {print $2}')
if [[ "$ANSIBLE_LINT_VERSION" =~ ^4 ]]
then
	echo "ansible-lint -c .ansible-lint-4 ${ANSIBLE_LINT_VERSION}..."
	ansible-lint -v -c .ansible-lint-4
elif test "${ANSIBLE_LINT_VERSION}" == "6.8.6"
then
	echo "ansible-lint ${ANSIBLE_LINT_VERSION}..."
	ansible-lint -v --offline -c .ansible-lint-6.8.6
elif test -f .ansible-lint-"${ANSIBLE_LINT_VERSION}"
then
	echo "ansible-lint -c .ansible-lint-${ANSIBLE_LINT_VERSION}..."
	ansible-lint -v -c .ansible-lint-"${ANSIBLE_LINT_VERSION}"
else
	echo "ansible-lint ${ANSIBLE_LINT_VERSION}..."
	ansible-lint -v
fi

echo "ansible-lint of variables..."
ansible-lint -v roles/*/vars/*.yml

echo "flake8..."
flake8 -v --exclude tests/output
