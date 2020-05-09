#! /bin/bash

. ~/.virtualenvs/molecule/bin/activate

cd /tmp/
ansible-playbook $OLDPWD/../../mafalb/ansible/playbooks/collection-init.yml -e collection=tests.testcollection
cd -

cd /tmp/tests/testcollection/roles
ansible-playbook $OLDPWD/playbooks/role-init.yml -e role=tests.testcollection.testrole -e "author='bla <blubb@example.com>'"
cd -

