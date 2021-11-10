# Copyright (c) 2021 Markus Falb <markus.falb@mafalb.at>
# GNU General Public License v3.0+
# see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt

from __future__ import (absolute_import, division, print_function)
try:
    from pkg_resources import Requirement as Pkgreq
except ImportError:
    Pkgreq = None
from ansible.module_utils.six import raise_from
from ansible.errors import (
    AnsibleFilterError,
)
import yaml
from os.path import dirname
__metaclass__ = type

datafile = open(dirname(__file__)
                + '/../../roles/virtualenv/vars/data.yml', 'r'
                )
data = yaml.load(datafile, Loader=yaml.FullLoader)
datafile.close()


def version2int(version):
    """Return a numeric representation of a version string in the form X.Y.Z

    I use this for sorting versions

    beta versions and release candidates return 0
    2.12.0rc1 -> 0
    2.12.0b2 -> 0
    """

    if not isinstance(version, str):
        raise AnsibleFilterError(
            "version is not a string but {type}".format(type=type(version))
        )
    if len(version.split('.')) != 3:
        raise AnsibleFilterError(
            "not a valid version string: {str}".format(str=version)
        )
    patch = version.split('.')[2]
    if not isinstance(int(patch[0]), int):
        raise AnsibleFilterError(
            "Not a valid patch version: {version}".format(version=patch)
        )
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
        raise AnsibleFilterError("Not a valid version: {x}".format(x=version))
    return value


def __major_minor_version(arg_req):
    """Take a pip requirement and return the best matching major.minor version

    arg_req is a string in the form of
    _ansible==2.11.6
    _ansible~=2.11.6
    etc.

    return a version string in the form of X.Y
    """

    try:
        # '_ansible' is not a valid pip name
        req = Pkgreq.parse(arg_req.replace('_ansible', 'ansible'))
    except Exception as e:
        raise_from(AnsibleFilterError(
            "not a valid pip specifier: {req}".format(req=arg_req)
        ), e)

    if req.name != 'ansible':
        raise AnsibleFilterError("not '_ansible': {str}".format(str=req.name))

    # exact version is requested
    if str(req.specifier).startswith('=='):
        return '.'.join(str(req.specifier).replace('==', '').split('.')[0:2])

    # in all other cases find possible versions
    all_versions = []
    # generate a list of all versions that are theoretically supported
    for majmin in data['latest_version']:
        for patch in range(
            0, int(data['latest_version'][majmin].split('.')[-1]) + 1
        ):
            all_versions.append(majmin + '.' + str(patch))
    possible_versions = [v for v in all_versions if req.specifier.contains(v)]
    try:
        latest_possible_version = sorted(
            possible_versions, key=version2int
        )[-1]
    except IndexError:
        # requested version is too old or too new
        raise AnsibleFilterError(
            "not a supported pip specifier: {req}".format(req=arg_req)
        )
    return '.'.join(latest_possible_version.split('.')[0:2])


def next_ansible_version(majmin):
    """Return the next version of ansible."""
    try:
        version = data['latest_version'][majmin]
    except (KeyError, TypeError):
        # majmin is probably in wrong format
        raise AnsibleFilterError(
            "not a supported major minor version: {v}".format(v=majmin)
        )
    patch = int(version.split('.')[2]) + 1
    return '.'.join(version.split('.')[0:2] + [str(patch)])


def __best_ansible_version(arg_req):
    """Take a pip requirement and return the latest major.minor.patch version

    arg_req is a string in the form of
    _ansible==2.11.6
    _ansible~=2.11.6
    etc.

    return a version string in the form of X.Y
    """

    try:
        # '_ansible' is not a valid pip name
        req = Pkgreq.parse(arg_req.replace('_ansible', 'ansible'))
    except Exception as e:
        raise_from(AnsibleFilterError(
            "not a valid pip specifier: {req}".format(req=arg_req)), e
        )

    if req.name != 'ansible':
        raise AnsibleFilterError("not '_ansible': {str}".format(str=req.name))

    # exact version is requested, expand to full version if necessary
    if str(req.specifier).startswith('=='):
        version = str(req.specifier).replace('==', '')
        if len(version.split('.')) == 3:  # e.g. 2.11.6
            return str(req.specifier).replace('==', '')
        elif len(version.split('.')) == 2:  # e.g. 2.11
            try:
                return data['latest_version'][version]
            except KeyError:
                raise AnsibleFilterError(
                    "version not supported: {v}".format(v=version)
                )

    # in all other cases find possible versions
    all_versions = []
    # generate a list of all versions that are theoretically supported
    for majmin in data['latest_version']:
        for patch in range(
            0, int(data['latest_version'][majmin].split('.')[-1]) + 1
        ):
            all_versions.append(majmin + '.' + str(patch))
    possible_versions = [v for v in all_versions if req.specifier.contains(v)]
    try:
        best_version = sorted(possible_versions, key=version2int)[-1]
    except IndexError:
        # requested version is too old or too new
        raise AnsibleFilterError(
            "not a supported pip specifier: {req}".format(req=arg_req)
        )
    return best_version


def __fix_ansible_pip_req(arg_req):
    """Take a pip requirement and fill in the correct name.

    arg_req is a string in the form of
    _ansible==2.11.6
    _ansible~=2.11.6
    etc.
    """

    if not isinstance(arg_req, str):
        raise AnsibleFilterError("arg_req is not string {type}".format(
            type=type(arg_req))
        )

    # '_ansible' is not a valid pip name
    req = Pkgreq.parse(arg_req.replace('_ansible', 'ansible'))

    specifier = str(req.specifier)
    # exact version is requested, expand to full version if necessary
    if specifier.startswith('=='):
        version = str(specifier).replace('==', '')
        if len(version.split('.')) == 2:  # e.g. 2.11
            try:
                specifier = '==' + data['latest_version'][version]
            except KeyError:
                raise AnsibleFilterError(
                    "version not supported: {v}".format(v=version)
                )

    # select the proper name for this version
    if __major_minor_version(arg_req) == '2.9':
        package = 'ansible'
    elif __major_minor_version(arg_req) == '2.10':
        package = 'ansible-base'
    else:
        package = 'ansible-core'
    return package + specifier


def __ansible_test_packages(version):
    """Return a list of ansible-test requirements"""
    return data['ansible_test_packages'][version]


def pip_package_list(arg_packages):
    """Return a list of pip packages."""
#    data = yaml.load(data, Loader=yaml.FullLoader)
    packages = [s for s in arg_packages if not s.startswith('_ansible')]
    matching = [s for s in arg_packages if s.startswith('_ansible')]
    for s in matching:
        # '_ansible' is not a valid pip name
        req = Pkgreq.parse(s.replace('_ansible', 'ansible'))
        if req.name == 'ansible':
            majmin = __major_minor_version(s)
            packages.append(__fix_ansible_pip_req(s))
        elif req.name == 'ansible_test':
            packages.extend(__ansible_test_packages(majmin))
    return packages


def best_version(arg_packages):
    """Return the latest possible ansible version."""
    for s in arg_packages:
        # we are not interested in the collections package
        if 'ansible' == s:
            continue
        # '_ansible' is not a valid pip name
        req = Pkgreq.parse(s.replace('_ansible', 'ansible'))
        if req.name == 'ansible':
            return __best_ansible_version(s)


class FilterModule(object):

    def filters(self):
        return {
            'fix_package_list': pip_package_list,
            'latest_ansible_version': best_version,  # remove
            'latest_version': best_version,          # remove
            'best_version': best_version,
            'next_version': next_ansible_version,
        }
