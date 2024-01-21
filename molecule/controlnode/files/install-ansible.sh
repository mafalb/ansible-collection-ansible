# Copyright (c) Markus Falb <markus.falb@mafalb.at>
# GNU General Public License v3.0+
# see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt


ansible-playbook -D /dev/stdin << PLAYBOOK
---

- hosts: localhost
  roles:
    - role: mafalb.ansible.python
    - role: mafalb.ansible.virtualenv
      packages:
        - _ansible==2.11

...
PLAYBOOK
