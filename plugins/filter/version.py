# Copyright (c) 2021 Markus Falb <markus.falb@mafalb.at>
# GNU General Public License v3.0+
# see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt

from __future__ import (absolute_import, division, print_function)

try:
    from pkg_resources import Requirement as Pkgreq
except ImportError:
    Pkgreq = None

from ansible.module_utils.six import raise_from
from ansible.errors import AnsibleError, AnsibleFilterError, AnsibleFilterTypeError
from ansible.module_utils._text import to_native
__metaclass__ = type


def version2int(version):
    """Return a numeric representation of a version string in the form X.Y.Z

    I use this for sorting versions

    beta versions and release candidates return 0
    2.12.0rc1 -> 0
    2.12.0b2 -> 0
    """

    if not isinstance(version, str):
        raise AnsibleFilterTypeError("version is not a string but {type}".format(type=type(version)))
    if len(version.split('.')) != 3:
        raise AnsibleFilterError("not a valid version string: {str}".format(str=version))
    patch = version.split('.')[2]
    if not isinstance(int(patch[0]), int):
        raise AnsibleFilterError("Not a valid patch version: {version}".format(version=patch))
    try:
        patch = int(patch)
    except ValueError:
        # assume it's a beta or prerelease version
        return 0
    try:
        value = (
            int(version.split('.')[0]) * 10000
            + int(version.split('.')[1]) * 100
            + patch
        )
    except ValueError:
        raise AnsibleFilterError("Not a valid version: {version}".format(version=version))
    return value


def major_minor_version(arg_req):
    """Take a pip requirement and return the best matching major.minor version

    arg_req is a string in the form of
    _ansible==2.11.6
    _ansible~=2.11.6
    etc.

    return a version string in the form of X.Y
    """

    latest_version = {
        '2.11': '2.11.6',
        '2.10': '2.10.15',
        '2.9': '2.9.27',
    }

    try:
        # '_ansible' is not a valid pip name
        req = Pkgreq.parse(arg_req.replace('_ansible', 'ansible'))
    except Exception as e:
        raise_from(AnsibleFilterTypeError("not a valid pip specifier: {req}".format(req=arg_req)), e)

    if req.name != 'ansible':
        raise AnsibleFilterError("not '_ansible': {str}".format(str=req.name))

    # exact version is requested
    if str(req.specifier).startswith('=='):
        return '.'.join(str(req.specifier).replace('==', '').split('.')[0:2])

    # in all other cases find possible versions
    all_versions = []
    # generate a list of all versions that are theoretically supported
    for majmin in latest_version:
        for patch in range(0, int(latest_version[majmin].split('.')[-1]) + 1):
            all_versions.append(majmin + '.' + str(patch))
    possible_versions = [v for v in all_versions if req.specifier.contains(v)]
    try:
        latest_possible_version = sorted(possible_versions, key=version2int)[-1]
    except IndexError:
        # requested version is too old or too new
        raise AnsibleFilterTypeError("not a supported pip specifier: {req}".format(req=arg_req))
    return '.'.join(latest_possible_version.split('.')[0:2])


def __latest_ansible_version(arg_req):
    """Take a pip requirement and return the latest major.minor.patch version

    arg_req is a string in the form of
    _ansible==2.11.6
    _ansible~=2.11.6
    etc.

    return a version string in the form of X.Y
    """

    latest_version = {
        '2.11': '2.11.6',
        '2.10': '2.10.15',
        '2.9': '2.9.27',
    }

    try:
        # '_ansible' is not a valid pip name
        req = Pkgreq.parse(arg_req.replace('_ansible', 'ansible'))
    except Exception as e:
        raise_from(AnsibleFilterTypeError("not a valid pip specifier: {req}".format(req=arg_req)), e)

    if req.name != 'ansible':
        raise AnsibleFilterError("not '_ansible': {str}".format(str=req.name))

    # exact version is requested
    if str(req.specifier).startswith('=='):
        majmin = '.'.join(str(req.specifier).replace('==', '').split('.')[0:2])
        return latest_version[majmin]

    # in all other cases find possible versions
    all_versions = []
    # generate a list of all versions that are theoretically supported
    for majmin in latest_version:
        for patch in range(0, int(latest_version[majmin].split('.')[-1]) + 1):
            all_versions.append(majmin + '.' + str(patch))
    possible_versions = [v for v in all_versions if req.specifier.contains(v)]
    try:
        latest_possible_version = sorted(possible_versions, key=version2int)[-1]
    except IndexError:
        # requested version is too old or too new
        raise AnsibleFilterTypeError("not a supported pip specifier: {req}".format(req=arg_req))
    return latest_possible_version


def fix_ansible_pip_req(arg_req):
    """Take a pip requirement and fill in the correct name.

    arg_req is a string in the form of
    _ansible==2.11.6
    _ansible~=2.11.6
    etc.
    """

    if not isinstance(arg_req, str):
        raise AnsibleFilterTypeError("arg_req is not string {type}".format(type=type(arg_req)))

    # '_ansible' is not a valid pip name
    req = Pkgreq.parse(arg_req.replace('_ansible', 'ansible'))

    # select the proper name for this version
    if major_minor_version(arg_req) == '2.9':
        package = 'ansible'
    elif major_minor_version(arg_req) == '2.10':
        package = 'ansible-base'
    else:
        package = 'ansible-core'
    return package + str(req.specifier)


def ansible_test_packages(version):
    """Return a list of ansible-test requirements"""
    packages = {
        '2.10': [
            'flake8',
            'antsibull-changelog',
            'pylint',
            'resolvelib',
            'toml',
            'voluptuous',
            'yamllint',
        ],
        '2.11': [
            'flake8',
            'antsibull-changelog',
            'pylint',
            'voluptuous',
            'yamllint',
        ],
        '2.9': [
            'flake8',
            'ntlm-auth',
            'pylint',
            'rstcheck',
            'sphinx',
            'virtualenv',
            'voluptuous',
            'yamllint',
        ],
    }
    return packages[version]


def pip_package_list(arg_packages):
    """Return a list of pip packages appropriate for the given version of ansible"""
    packages = [s for s in arg_packages if not s.startswith('_ansible')]
    matching = [s for s in arg_packages if s.startswith('_ansible')]
    for s in matching:
        # '_ansible' is not a valid pip name
        req = Pkgreq.parse(s.replace('_ansible', 'ansible'))
        if req.name == 'ansible':
            majmin = major_minor_version(s)
            packages.append(fix_ansible_pip_req(s))
        elif req.name == 'ansible_test':
            packages.extend(ansible_test_packages(majmin))
    return packages


def latest_ansible_version(arg_packages):
    """Return a list of pip packages appropriate for the given version of ansible"""
    for s in arg_packages:
        # '_ansible' is not a valid pip name
        req = Pkgreq.parse(s.replace('_ansible', 'ansible'))
        if req.name == 'ansible':
            return __latest_ansible_version(s)


def filter_pipver(version):
    version = str(version)
    try:
        if (version.count('.') == 2):
            return version
        elif (version.count('.') == 1):
            return version + ".*"
        elif (version.count('.') == 0):
            return version + ".*"
        else:
            raise AnsibleError('Bad version number: %s' % version)
    except Exception as e:
        raise_from(AnsibleError('Error in filter_pipver, ',
                   'this was original exception: %s' % to_native(e)), e)


def filter_semver(version):
    version = str(version)
    try:
        if (version.count('.') == 2):
            return version.replace('*', '0')
        elif (version.count('.') == 1):
            return (version + ".0").replace('*', '0')
        elif (version.count('.') == 0):
            return (version + ".0.0").replace('*', '0')
        else:
            raise AnsibleError('Wrong version number: %s' % version)
    except Exception as e:
        raise_from(AnsibleError('Error in filter_semver, ',
                   'this was original exception: %s' % to_native(e)), e)


class FilterModule(object):

    def filters(self):
        return {
            'pipver': filter_pipver,
            'semver': filter_semver,
            'fix_package_list': pip_package_list,
            'latest_ansible_version': latest_ansible_version,
        }
