..
  GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
  SPDX-License-Identifier: GPL-3.0-or-later
  SPDX-FileCopyrightText: 2020, Felix Fontein

.. _ansible_collections.mafalb.ansible.docsite.virtualenv_role:

Role mafalb.ansible.virtualenv
==============================

Basic Usage
-----------

.. code-block:: yaml+jinja

    - roles:
        - role: mafalb.ansible.virtualenv
          virtualenv_packages:
            - ansible-core==2.11
            - ansible-lint>=5
..

As seen above, I give it a list of pip requirements.
Under the hood some unexpected things will happen

- The major.minor.patch version of the targeted ansible is determined
- A pip constraints file is created, with constraints from ansible-test

When you run ansible locally, i.e. not from venv or docker


.. code-block:: shell

    (venv) $ ansible-test sanity --local --requirements
    (venv) $ ansible-test units --local --requirements
    (venv) $ ansible-test integration --local --requirements
..

In this case a lot of packages are installed. Version specific constraints were used while doing the install in the first place so in theory no packages are reinstalled with different version.

A warning though. This is prone to security issues due to old packages.

If you don't want to use the constraints feature, use

.. code-block:: yaml+jinja

    - roles:
        - role: mafalb.ansible.virtualenv
          virtualenv_constraints: false
          virtualenv_packages:
            - ansible-core==2.11
            - ansible-lint>=5
..
