#!/bin/bash -eu

set -e
set -x

# Copyright (c) Markus Falb <markus.falb@mafalb.at>
# GNU General Public License v3.0+
# see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt

if test "$#" -gt 0
then

        if test "$1" == 'requirements'
        then
                args[0]=--requirements
                shift
        fi
fi

mkdir -p "tests/output/doc"
ABSPATH=$(cd ../../; dirname "$(pwd)")
if test -n "${ANSIBLE_COLLECTIONS_PATH}"; then
	OLD_ANSIBLE_COLLECTIONS_PATH=${ANSIBLE_COLLECTIONS_PATH}
fi
export ANSIBLE_COLLECTIONS_PATH="${ABSPATH}:/tmp/collections"

antsibull-docs lint-collection-docs --plugin-docs --no-skip-rstcheck .
antsibull-docs sphinx-init --use-current --copyright "Markus Falb (c) <markus.falb@mafalb.at> GPL-3.0-or-later" --dest-dir tests/output/doc mafalb.ansible
cd tests/output/doc
if test "${args[0]}" = "--requirements"; then
	if test -z "${VIRTUAL_ENV}"; then
		exit 1
	fi
	pip install -r requirements.txt -c "${VIRTUAL_ENV}"/constraints.txt
fi
./build.sh

if test -n "${OLD_ANSIBLE_COLLECTIONS_PATH}"; then
	export -n ANSIBLE_COLLECTIONS_PATH
fi
