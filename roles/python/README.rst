..
  Copyright (c) Markus Falb <markus.falb@mafalb.at>
  GNU General Public License v3.0+
  see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt

.. _ansible_collections.mafalb.ansible.docsite.python_role:

mafalb.ansible.python
=====================

An ansible role for installing python.

Basic Usage
-----------

.. code-block:: yaml+jinja

  - name: Install the default python
    hosts: localhost
    roles:
      - role: mafalb.ansible.python
..

.. code-block:: yaml+jinja

  - name: Install a specific version of  python
    hosts: localhost
    roles:
      - role: mafalb.ansible.python
        python_version: '3.11'
..

License
-------

Copyright (c) Markus Falb <markus.falb@mafalb.at>

GPL-3.0-or-later
