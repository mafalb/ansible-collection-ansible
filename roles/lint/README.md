# Ansible Role - mafalb.ansible.lint

A Role for installing ansible-lint either via native package manager or via pip in a virtualenv.

## Basic Usage

```yaml
- name: install ansible-lint
  hosts: localhost
  roles:
  - role: mafalb.ansible.lint
```

## Variables

Variables are optional. Only specify them if you want to override the defaults.

---

```ansible_lint_update``` Set if you want to update an existent installation of molecule

```yaml
ansible_lint_update: true
```

---

```ansible_lint_virtualenv``` set the path to the virtualenv. Specify a absolute path. ```~/something``` will not work.

```yaml
ansible_lint_virtualenv: "{{ ansible_user_dir }}/.virtualenvs/testvenv
```

## License

Copyright (c) 2020,2021 Markus Falb <markus.falb@mafalb.at>

GPL-3.0-or-later
