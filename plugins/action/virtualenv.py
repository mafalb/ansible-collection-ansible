# Copyright (c) Markus Falb <markus.falb@mafalb.at>
# GNU General Public License v3.0+
# see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.plugins.action import ActionBase
from ansible.plugins.filter.core import to_json
from ansible_collections.mafalb.ansible.plugins.filter.ansible import best_version
from ansible_collections.mafalb.ansible.plugins.filter.ansible import (
    pip_package_list as fix_package_list)
from ansible.utils.display import Display

display = Display()


class ActionModule(ActionBase):

    def python_info(self, executable, task_vars=None):
        module_args = {}
        module_args['executable'] = executable
        module_return = {'failed': True}
        display.debug("Python interpreter %s" % to_json(executable))
        module_return = self._execute_module(module_name='mafalb.ansible.python_info',
                                             module_args=module_args,
                                             task_vars=task_vars)
        return module_return

    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)
        module_args = self._task.args.copy()
        module_return = {
            'results': [
                {'item': 'python_info1'},
                {'item': 'create_virtualenv'},
                {'item': 'python_info2'},
                {'item': 'install_packages'}
            ]
        }

        display.debug("Variables %s" % to_json(task_vars))

        ansible_python_executable = task_vars.get('ansible_python')['executable']
        python_executable = self._task.args.get('executable', ansible_python_executable)

        # Get info about the targeted python interpreter
        # Note that the virtualenv may exist already and could have been created with
        # another interpreter. However, We do not recreate virtualenvs.
        #
        module_return['results'][0] = self.python_info(executable=python_executable,
                                                       task_vars=task_vars)

        python_version = self._task.args.get('python_version')
        packages = self._task.args.get('name')
        fixed_packages = fix_package_list(packages, python_version)
        best_ansible_version = best_version(packages, python_version)

        display.debug("Python interpreter %s" % to_json(python_version))
        display.debug("Python interpreter %s" % to_json(packages))
        display.debug("Python interpreter %s" % to_json(fixed_packages))
        display.debug("Python interpreter %s" % to_json(best_ansible_version))

        # create the virtualenv
        module_args_copy = dict(module_args)
        module_args_copy['name'] = ['wheel']
        module_return['results'][1] = self._execute_module(module_name='pip',
                                                           module_args=module_args_copy,
                                                           task_vars=task_vars)
        del module_args_copy
        if 'failed' not in module_return['results'][1]:
            module_return['results'][1]['failed'] = False

        # if the virtualenv already existed, the virtualenv interpreter could
        # be different from python_version
        #
        virtualenv = module_return['results'][1]['virtualenv']
        module_return['results'][2] = self.python_info(executable=virtualenv + '/bin/python',
                                                       task_vars=task_vars)

        # install the packages
        module_return['results'][3] = self._execute_module(module_name='pip',
                                                           module_args=module_args,
                                                           task_vars=task_vars)
        if 'failed' not in module_return['results'][3]:
            module_return['results'][3]['failed'] = False

        module_return['failed'] = False
        return dict(module_return)
