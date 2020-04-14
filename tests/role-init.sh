#! /bin/bash

. ~/.virtualenvs/molecule/bin/activate

cd /tmp
ansible-playbook $OLDPWD/playbooks/role-init.yml -e namespace=tests -e collection=false -e role_name=testrole -e "author='bla <blubb@example.com>'"
cd -

