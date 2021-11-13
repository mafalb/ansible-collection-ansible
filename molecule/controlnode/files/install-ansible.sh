# Copyright (c) 2019-2021 Markus Falb <markus.falb@mafalb.at>
# GNU General Public License v3.0+
# see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt


ANSIBLE_COLLECTIONS_PATHS=/root ansible-playbook -D /dev/stdin << PLAYBOOK
---

- hosts: localhost
  roles:
    - role: mafalb.ansible.python
    - role: mafalb.ansible.virtualenv
      packages:
        - _ansible==2.11

...
PLAYBOOK
