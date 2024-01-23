# Copyright (c) Markus Falb <markus.falb@mafalb.at>
# GNU General Public License v3.0+
# see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt

from __future__ import (absolute_import, division, print_function)
import sys
import yaml

try:
    from packaging.requirements import Requirement as Pkgreq
    from packaging.version import Version as Pkgver
except ImportError:  # make ansible-test sanity happy
    Pkgreq = None
from ansible.module_utils.six import raise_from
from ansible.errors import (
    AnsibleFilterError,
)
from os.path import dirname


__metaclass__ = type

from ansible.utils.display import Display
display = Display()

datafile = open(dirname(__file__)
                + '/../../roles/virtualenv/vars/data.yml', 'r'
                )
data = yaml.load(datafile, Loader=yaml.Loader)
datafile.close()


def __parse_requirement(arg_req):
    """Take a requirement in text representation and
    Return appropiate Specifier Ojects and functions.

    Do not use. Obsolete.
    """

    try:
        # '_ansible' is not a valid pip name
        req = Pkgreq(arg_req.replace('_ansible', 'ansible'))
    except Exception as e:
        raise_from(AnsibleFilterError(
            "not a valid pip specifier: {s} {ss}".format(s=arg_req,
                                                         ss=str(e))), e
                   )
    name = req.name
    spec = req.specifier
    specstr = str(req.specifier)
    contains_function = req.specifier.contains
    return name, spec, specstr, contains_function


def __parse_requirement_new(arg_req):
    """Take a requirement in text representation and
    Return appropiate Specifier Ojects and functions.
    """

    try:
        req = Pkgreq(arg_req)
    except Exception as e:
        raise_from(AnsibleFilterError("not a valid pip specifier: {s} {ss}".format(s=arg_req, ss=str(e))), e)
    name = req.name
    spec = req.specifier
    specstr = str(req.specifier)
    contains_function = req.specifier.contains
    return name, spec, specstr, contains_function


def __version2int(version):
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

    name, spec, specstr, req_contains = __parse_requirement(arg_req)
    if name != 'ansible':
        raise AnsibleFilterError("not '_ansible': {str}".format(str=name))

    # exact version is requested
    if specstr.startswith('=='):
        return '.'.join(specstr.replace('==', '').split('.')[0:2])

    # in all other cases find possible versions
    all_versions = []
    # generate a list of all versions that are theoretically supported
    for majmin in data['latest_ansible_version']:
        if (python_version
                and python_version not in data['python_versions'][majmin]):
            # ansible X.Y is not compatible with requested python
            continue
        for patch in range(
            0, int(data['latest_ansible_version'][majmin].split('.')[-1]) + 1
        ):
            all_versions.append(majmin + '.' + str(patch))
    possible_versions = [v for v in all_versions if req_contains(v)]
    try:
        latest_possible_version = sorted(
            possible_versions, key=__version2int
        )[-1]
    except IndexError:
        # requested version is too old or too new
        raise AnsibleFilterError(
            "not a supported pip specifier: {req}".format(req=arg_req)
        )
    return '.'.join(latest_possible_version.split('.')[0:2])


def __ansible_test_packages(version):
    """Return a list of ansible-test requirements"""
    try:
        return data['ansible_test_packages'][version]
    except Exception as e:
        raise AnsibleFilterError(
            "No key in ansible_test_packages: {s}".format(s=str(e)))


def next_ansible_version(majmin):
    """Return the next version of ansible."""
    try:
        version = data['latest_ansible_version'][majmin]
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
    Do not use. Obsolete.
    """

    if not python_version:
        python_version = (str(sys.version_info.major) + '.' +
                          str(sys.version_info.minor))

    for s in arg_packages:
        # we are interested in the _ansible pseudo package
        if s.startswith('_ansible') and not s.startswith('_ansible_test'):
            break
    name, spec, specstr, req_contains = __parse_requirement(s)
    if name != 'ansible':
        raise AnsibleFilterError("There is no '_ansible' in package list: {str}".format(str=name))

    # exact version is requested, expand to full version if necessary
    # it could be that that's not compatible with requested python version
    if specstr.startswith('=='):
        version = specstr.replace('==', '')
        if len(version.split('.')) == 3:  # e.g. 2.11.6
            majmin = '.'.join(version.split('.')[0:2])
            if python_version in data['python_versions'][majmin]:
                return version
            else:
                raise AnsibleFilterError(
                    "version not supported: {v}".format(v=version)
                )
        elif len(version.split('.')) == 2:  # e.g. 2.11
            try:
                if python_version in data['python_versions'][version]:
                    return data['latest_ansible_version'][version]
            except KeyError:
                raise AnsibleFilterError(
                    "version not supported: {v}".format(v=version)
                )

    # in all other cases find possible versions
    all_versions = []
    # generate a list of all versions that are theoretically supported
    for majmin in data['latest_ansible_version']:
        if (python_version
                and python_version not in data['python_versions'][majmin]):
            # ansible X.Y is not compatible with requested python
            continue
        for patch in range(
            0, int(data['latest_ansible_version'][majmin].split('.')[-1]) + 1
        ):
            all_versions.append(majmin + '.' + str(patch))
    possible_versions = [v for v in all_versions if req_contains(v)]
    try:
        best_version = sorted(possible_versions, key=__version2int)[-1]
    except IndexError:
        # requested version is too old or too new
        raise AnsibleFilterError(
            "not a supported python interpreter for: {req}".format(req=s)
        )
    return best_version


# A placeholder to make documentation happy
#
def fix_package_list(arg_packages, python_version=None):
    """Alias for P(pip_package_list#filter)"""
    pass


def pip_package_list(arg_packages, python_version=None):
    """Take a pip requirement and fill in the correct name.

    arg_req is a string in the form of
    _ansible==2.11.6
    _ansible~=2.11.6
    etc.

    Do not use. Obsolete.
    """

    if not isinstance(arg_packages, list):
        raise AnsibleFilterError("arg_packages is not list {type}".format(
            type=type(arg_packages))
        )

    if not python_version:
        python_version = (str(sys.version_info.major) + '.' +
                          str(sys.version_info.minor))

    packages = [s for s in arg_packages if not s.startswith('_ansible')]
    matching = [s for s in arg_packages if s.startswith('_ansible')]
    for s in matching:
        name, spec, specstr, req_contains = __parse_requirement(s)
        if name == 'ansible':
            majmin = __major_minor_version(s)
    for s in matching:
        name, spec, specstr, req_contains = __parse_requirement(s)
        if name == 'ansible':
            specifier = specstr
            # exact version is requested, expand to full version if necessary
            if specifier.startswith('=='):
                version = specstr.replace('==', '')
                if len(version.split('.')) == 2:  # e.g. 2.11
                    try:
                        specifier = ('==' +
                                     data['latest_ansible_version'][version])
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


def __majmin(version):
    """Parse the argument and return major.minor version."""
    if not isinstance(version, str):
        raise AnsibleFilterError("Not a string {s}".format(s=version))
    if not version.split('.')[-1]:
        raise AnsibleFilterError("Not a valid version {s}".format(s=version))
    if len(version.split('.')) == 2:
        return version
    elif len(version.split('.')) == 3:
        return '.'.join(version.split('.')[0:2])
    else:
        raise AnsibleFilterError("Not a valid version {s}".format(s=version))


def __gen_new_ansible_versions():
    """Return a list of all newer major.minor versions of ansible.

    Newer means that ansible-base or ansible-core already existed.
    """
    all_versions = []
    for majmin in data['latest_ansible_version']:
        if majmin == '2.9':
            continue
        for patch in range(0, int(data['latest_ansible_version'][majmin].split('.')[-1]) + 1):
            if (majmin == '2.10' and patch < 8):
                continue
            all_versions.append(majmin + '.' + str(patch))
        if majmin in data['ansible_rc_versions']:
            for rc_version in data['ansible_rc_versions'][majmin]:
                all_versions.append(rc_version)
    return all_versions


def __gen_old_ansible_versions():
    """Return a list of all old major.minor versions of ansible.

    Old means that ansible-base or ansible-core did not exist.
    """
    all_versions = []
    for majmin in ('2.9', '2.10'):
        for patch in range(0, int(data['latest_ansible_version'][majmin].split('.')[-1]) + 1):
            if (majmin == '2.10' and patch > 7):
                continue
            all_versions.append(majmin + '.' + str(patch))
    return all_versions


def __is_old_ansible(arg_spec):
    """Detect if ansible designates an old ansible package
    or the new style ansible collections packages.

    Old means that ansible-base or ansible-core did not exist.
    New means that ansible-base or ansible-core already existed.

    e.g.

    ==2.9 is an old style package.
    ==2.10.2 is an old style package.
    ==2.10.8 is not an old style package.
    """
    new_versions = __gen_new_ansible_versions()
    for version in new_versions:
        if Pkgver(version) in arg_spec:
            # if we find one new version, we are done
            return False
    # we do not need to search for an old version
    # if nothing matches assume new version
    return True


def __detect_ansible_package(arg_packages):
    has_ansible = 0
    ansible_package = 'ansible-core'
    for requirement in arg_packages:
        name, spec, specstr, f = __parse_requirement_new(requirement)
        if name == 'ansible-core':
            has_ansible += 1
            ansible_package = 'ansible-core'
        elif name == 'ansible-base':
            has_ansible += 1
            ansible_package = 'ansible-base'
        elif name == 'ansible' and __is_old_ansible(spec):
            # Assume new style ansible package
            has_ansible += 1
            ansible_package = 'ansible'

    if (has_ansible < 2):
        return ansible_package
    else:
        raise AnsibleFilterError("Collision detected: Specify only one of ansible-core/ansible-base/ansible are specified {s}".format(s=arg_packages))


def package_list(arg_packages, python_version=None):
    """Inject major.minor.patch version of ansible into pip requirement lists.

    Return major.minor version of ansible
    """
    if not python_version:
        python_version = (str(sys.version_info.major) + '.' +
                          str(sys.version_info.minor))
    ansible_package = __detect_ansible_package(arg_packages)
    for requirement in arg_packages:
        name, spec, specstr, req_contains = __parse_requirement_new(requirement)
        if name == ansible_package:
            break
    # find all possible versions
    if ansible_package == 'ansible':
        all_versions = __gen_old_ansible_versions()
    else:
        all_versions = __gen_new_ansible_versions()

    # Filter out versions not supported by specific python version
    #
    all_versions = [v for v in all_versions if python_version in data['python_versions'][__majmin(v)]]

    possible_versions = [v for v in all_versions if req_contains(v)]
    try:
        best_version = sorted(possible_versions, key=__version2int)[-1]
    except IndexError:
        # requested version is too old or too new
        raise AnsibleFilterError("not a supported python interpreter {a} {p}".format(a=all_versions, p=possible_versions))

    # modifying directly, does it work?
    #
    for i in range(len(arg_packages)):
        if (arg_packages[i] == ansible_package + specstr):
            arg_packages[i] = ansible_package + '==' + best_version

    # Return major.minor only
    #
    return best_version
    # return __majmin(best_version)


class FilterModule(object):

    def filters(self):
        return {
            'package_list': package_list,
            'fix_package_list': pip_package_list,
            'best_version': best_version,
            'next_version': next_ansible_version,
        }
