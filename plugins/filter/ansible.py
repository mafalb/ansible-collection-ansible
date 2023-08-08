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
data = yaml.load(datafile, Loader=yaml.Loader)
datafile.close()


def parse_requirement(arg_req):
    try:
        # '_ansible' is not a valid pip name
        req = Pkgreq.parse(arg_req.replace('_ansible', 'ansible'))
    except Exception as e:
        raise_from(AnsibleFilterError(
            "not a valid pip specifier: {s} {ss}".format(s=arg_req, ss=str(e))), e
        )
    if hasattr(req, 'name'):
        name = req.name
        spec = req.specifier
        specstr = str(req.specifier)
        contains_function = req.specifier.contains
    elif hasattr(req, 'key'):
        name = req.key
        if req.specs:
            spec = req.specs[0]
            specstr = spec[0] + spec[1]
        else:
            spec = None
            specstr = ''
        contains_function = req.__contains__
    else:
        raise AnsibleFilterError("no valid Requirements {x}".format(x=req))
    return name, spec, specstr, contains_function


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
    if len(version.split('.')) == 2:
        # fix it
        version = version + '.0'
    if len(version.split('.')) != 3:
        # should not happen
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


def __major_minor_version(arg_req, python_version=None):
    """Take a pip requirement and return the best matching major.minor version

    arg_req is a string in the form of
    _ansible==2.11.6
    _ansible~=2.11.6
    etc.

    return a version string in the form of X.Y
    """

    name, spec, specstr, req_contains = parse_requirement(arg_req)
    if name != 'ansible':
        raise AnsibleFilterError("not '_ansible': {str}".format(str=name))

    # exact version is requested
    if specstr.startswith('=='):
        return '.'.join(specstr.replace('==', '').split('.')[0:2])

    # in all other cases find possible versions
    all_versions = []
    # generate a list of all versions that are theoretically supported
    for majmin in data['latest_version']:
        if (python_version
                and python_version not in data['python_versions'][majmin]):
            # ansible X.Y is not compatible with requested python
            continue
        for patch in range(
            0, int(data['latest_version'][majmin].split('.')[-1]) + 1
        ):
            all_versions.append(majmin + '.' + str(patch))
    possible_versions = [v for v in all_versions if req_contains(v)]
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


def best_version(arg_packages, python_version=None):
    """Take a pip requirement and return the latest major.minor.patch version

    arg_req is a list, e.g.
    [ '_ansible==2.11.6', 'ansible', '_ansible_test' ]

    return a version string in the form of X.Y.Z
    """

    for s in arg_packages:
        # we are interested in the _ansible pseudo package
        if s.startswith('_ansible') and not s.startswith('_ansible_test'):
            break
    name, spec, specstr, req_contains = parse_requirement(s)
    if name != 'ansible':
        raise AnsibleFilterError("not '_ansible': {str}".format(str=name))

    # exact version is requested, expand to full version if necessary
    # it could be that that's not compatible with requested python version
    if specstr.startswith('=='):
        version = specstr.replace('==', '')
        if len(version.split('.')) == 3:  # e.g. 2.11.6
            return version
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
        if (python_version
                and python_version not in data['python_versions'][majmin]):
            # ansible X.Y is not compatible with requested python
            continue
        for patch in range(
            0, int(data['latest_version'][majmin].split('.')[-1]) + 1
        ):
            all_versions.append(majmin + '.' + str(patch))
    possible_versions = [v for v in all_versions if req_contains(v)]
    try:
        best_version = sorted(possible_versions, key=version2int)[-1]
    except IndexError:
        # requested version is too old or too new
        raise AnsibleFilterError(
            "not a supported pip specifier: {req}".format(req=s)
        )
    return best_version


def pip_package_list(arg_packages, python_version=None):
    """Take a pip requirement and fill in the correct name.

    arg_req is a string in the form of
    _ansible==2.11.6
    _ansible~=2.11.6
    etc.
    """

    if not isinstance(arg_packages, list):
        raise AnsibleFilterError("arg_packages is not list {type}".format(
            type=type(arg_packages))
        )

    packages = [s for s in arg_packages if not s.startswith('_ansible')]
    matching = [s for s in arg_packages if s.startswith('_ansible')]
    for s in matching:
        name, spec, specstr, req_contains = parse_requirement(s)
        if name == 'ansible':
            majmin = __major_minor_version(s)
            specifier = specstr
            # exact version is requested, expand to full version if necessary
            if specifier.startswith('=='):
                version = specstr.replace('==', '')
                if len(version.split('.')) == 2:  # e.g. 2.11
                    try:
                        specifier = '==' + data['latest_version'][version]
                    except KeyError:
                        raise AnsibleFilterError(
                            "version not supported: {v}".format(v=version)
                        )
            # select the proper name for this version
            if __major_minor_version(s, python_version) == '2.9':
                package = 'ansible'
            elif __major_minor_version(s, python_version) == '2.10':
                package = 'ansible-base'
            else:
                package = 'ansible-core'
            packages.append(package + specifier)
        elif name == 'ansible_test':
            packages.extend(__ansible_test_packages(majmin))
    return packages


def __ansible_test_packages(version):
    """Return a list of ansible-test requirements"""
    return data['ansible_test_packages'][version]


class FilterModule(object):

    def filters(self):
        return {
            'fix_package_list': pip_package_list,
            'latest_ansible_version': best_version,  # remove
            'latest_version': best_version,          # remove
            'best_version': best_version,
            'next_version': next_ansible_version,
        }
