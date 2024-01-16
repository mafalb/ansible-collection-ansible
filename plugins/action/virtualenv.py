# Copyright (c) Markus Falb <markus.falb@mafalb.at>
# GNU General Public License v3.0+
# see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
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

        self._supports_check_mode = True
        super(ActionModule, self).run(tmp, task_vars)
        module_args = self._task.args.copy()

        # display.debug("Variables %s" % to_json(task_vars))

        ansible_python_executable = task_vars.get('ansible_python')['executable']

        # Note that the virtualenv may exist already and could have been created with
        # another interpreter. If the virtualenv already exists override
        # python_executable
        #
        virtualenv = self._task.args.get('virtualenv')
        if (os.path.exists(os.path.join(virtualenv, 'bin', 'activate')) and
                os.path.exists(os.path.join(virtualenv, 'bin', 'python'))):
            python_executable = os.path.join(virtualenv, 'bin', 'python')
        else:
            python_executable = self._task.args.get('virtualenv_python', ansible_python_executable)

        # Get info about the targeted python interpreter
        ret0 = self.python_info(executable=python_executable, task_vars=task_vars)
        ret0['item'] = 'python_info1'

        display.v("python_info1 %s" % to_json(ret0))

        # create the virtualenv
        display.v("Virtualenv %s" % to_json(self._task.args.get('virtualenv')))
        module_args['virtualenv_command'] = python_executable + " -m venv"
        module_args_copy = dict(module_args)
        module_args_copy['name'] = ['wheel']
        ret1 = self._execute_module(module_name='pip', module_args=module_args_copy, task_vars=task_vars)
        ret1['item'] = 'create_virtualenv'
        del module_args_copy
        if 'failed' not in ret1:
            ret1['failed'] = False
        display.v("Create virtualenv %s" % to_json(ret1))

        packages = self._task.args.get('name')
        display.v("Packages %s" % to_json(packages))

        python_version = ret0['version']['majmin']
        display.v("Python version %s" % to_json(python_version))

        fixed_packages = fix_package_list(packages, python_version)
        display.v("Fixed packages %s" % to_json(fixed_packages))
        module_args['name'] = fixed_packages

        best_ansible_version = best_version(packages, python_version)
        display.v("Best ansible version %s" % to_json(best_ansible_version))

        # install the packages
        ret2 = self._execute_module(module_name='pip', module_args=module_args, task_vars=task_vars)
        ret2['item'] = 'install_packages'
        if 'failed' not in ret2:
            ret2['failed'] = False

        module_return = {}
        module_return['failed'] = ret2['failed']
        if 'changed' in ret2:
            module_return['changed'] = ret2['changed']
        module_return['results'] = [ret0, ret1, ret2]
        return dict(module_return)
