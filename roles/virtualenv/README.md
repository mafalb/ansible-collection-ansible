# Ansible Role - mafalb.ansible.virtualenv

Install ansible via pip inside a virtualenv.

## Basic Usage

```yaml
- roles:
    - role: mafalb.ansible.virtualenv
      packages:
        - _ansible==2.11
        - ansible-lint>=5
        - _ansible_test
```

As seen above, I give it a list of pip requirements. Packages with underscores are treated special and are substituted by the role.

_ansible gets substituted by ansible or ansible-core or ansible-base depending on the requested version.
_ansible-test gets substituted by a list of packages that are necessary for running ansible-test in the original virtualenv, i.e. not running ansible-test in a container or venv. In addition version specific constraints are used so that no packages are reinstalled with different version when you call with `ansible-test --requirements`.

## License

Copyright (c) 2020,2021 Markus Falb <markus.falb@mafalb.at>

GPL-3.0-or-later
