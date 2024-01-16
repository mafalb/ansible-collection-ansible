# An ansible role for installing python2 [![Build Status](https://travis-ci.com/mafalb/ansible-python2.svg?branch=master)](https://travis-ci.com/mafalb/ansible-python2)

|Distribution          |Python 2|Python 3|default|
|----------------------|--------|--------|-------|
|Ubuntu 16.04 Xenial|python|python3|python3|
|Ubuntu 18.04 Bionic|python|python3|python3|
|RHEL 6|python|-|python|
|RHEL 7|python|python3|python|
|RHEL 8|python2|python3|python3|
|Fedora|python2|python3|python3|

https://bugzilla.redhat.com/show_bug.cgi?id=1932650
https://bugzilla.redhat.com/bugzilla/show_bug.cgi?id=2093589

## Basic Usage

```yaml
- hosts: localhost
  roles:
  - role: mafalb.python.python
  - role: mafalb.python/pip
```

## Variables

```python_package```

```yaml
python2_pip_upgrade: false
```

if set it will do a pip install --upgrade pip .

## License

GPLv3
