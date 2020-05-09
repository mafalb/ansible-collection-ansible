#! /bin/bash

. ~/.virtualenvs/molecule/bin/activate

cd /tmp
ansible-playbook $OLDPWD/playbooks/role-init.yml -e role=tests.testrole -e "author='bla <blubb@example.com>'"
cd -

