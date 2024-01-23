#!/bin/bash -eu

set -e
# Copyright (c) Markus Falb <markus.falb@mafalb.at>
# GNU General Public License v3.0+
# see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt

mkdir -p "tests/output/doc"
ABSPATH=$(cd ../../; dirname "$(pwd)")
if test -n "${ANSIBLE_COLLECTIONS_PATH}"; then
	OLD_ANSIBLE_COLLECTIONS_PATH=${ANSIBLE_COLLECTIONS_PATH}
fi
export ANSIBLE_COLLECTIONS_PATH="${ABSPATH}"

antsibull-docs lint-collection-docs --plugin-docs --no-skip-rstcheck .
antsibull-docs sphinx-init --use-current --dest-dir tests/output/doc mafalb.ansible
cd tests/output/doc
pip install -r requirements.txt -c ~/.virtualenvs/molecule/constraints.txt
./build.sh

if test -n "${OLD_ANSIBLE_COLLECTIONS_PATH}"; then
	export -n ANSIBLE_COLLECTIONS_PATH
fi
