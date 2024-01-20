# Copyright (c) Markus Falb <markus.falb@mafalb.at>
# GNU General Public License v3.0+
# see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import tempfile
import shutil

from ansible import constants as C
from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError, AnsibleFileNotFound, AnsibleAction, AnsibleActionFail
from ansible.module_utils.common.text.converters import to_bytes, to_text
from ansible.plugins.filter.core import to_json
from ansible.template import generate_ansible_template_vars, AnsibleEnvironment
from ansible_collections.mafalb.ansible.plugins.filter.ansible import package_list, __majmin as majmin
from ansible.utils.display import Display

display = Display()


class ActionModule(ActionBase):

    TRANSFERS_FILES = True
    DEFAULT_NEWLINE_SEQUENCE = "\n"

    def get_python_executable(self, task_vars=None):

        # Note that the virtualenv may exist already and could have been created with
        # another interpreter. If the virtualenv already exists override
        # python_executable
        #
        virtualenv = self._task.args.get('virtualenv')
        ansible_python_executable = task_vars.get('ansible_python')['executable']
        if (os.path.exists(os.path.join(virtualenv, 'bin', 'activate')) and
                os.path.exists(os.path.join(virtualenv, 'bin', 'python'))):
            python_executable = os.path.join(virtualenv, 'bin', 'python')
        else:
            python_executable = self._task.args.get('virtualenv_python', ansible_python_executable)
        return python_executable

    def set_virtualenv_command(self, task_vars=None):

        try:
            self._task.args['virtualenv_command'] = self.get_python_executable(task_vars=task_vars) + " -m venv"
        except Exception as e:
            raise AnsibleActionFail("Could not get python interpreter {e}".format(e=e))

    def python_info(self, executable, task_vars=None):
        module_args = {}
        module_args['executable'] = executable
        module_return = {'failed': True}
        display.debug("Python interpreter %s" % to_json(executable))
        module_return = self._execute_module(module_name='mafalb.ansible.python_info',
                                             module_args=module_args,
                                             task_vars=task_vars)
        return module_return

    def constraints(self, constraints_src=None, task_vars=None):

        module_return = {}

        # assign to local vars for ease of use
        source = constraints_src
        virtualenv = self._task.args.get('virtualenv', None)
        dest = virtualenv + '/constraints.txt'
        state = self._task.args.get('state', None)
        newline_sequence = self._task.args.get('newline_sequence', self.DEFAULT_NEWLINE_SEQUENCE)
        output_encoding = self._task.args.get('output_encoding', 'utf-8') or 'utf-8'

        wrong_sequences = ["\\n", "\\r", "\\r\\n"]
        allowed_sequences = ["\n", "\r", "\r\n"]

        # We need to convert unescaped sequences to proper escaped sequences for Jinja2
        if newline_sequence in wrong_sequences:
            newline_sequence = allowed_sequences[wrong_sequences.index(newline_sequence)]

        try:
            if state is not None:
                raise AnsibleActionFail("'state' cannot be specified on a template")
            if constraints_src is None:
                raise AnsibleActionFail("src is required")
            if dest is None:
                raise AnsibleActionFail("dest is required")
            if virtualenv is None:
                raise AnsibleActionFail("virtualenv is required")
            elif newline_sequence not in allowed_sequences:
                raise AnsibleActionFail("newline_sequence needs to be one of: \n, \r or \r\n")
            else:
                try:
                    source = self._find_needle('templates', source)
                    display.debug("template source: {s}".format(s=source))
                except AnsibleError as e:
                    raise AnsibleActionFail(to_text(e))
            # Get vault decrypted tmp file
            try:
                tmp_source = self._loader.get_real_file(source)
            except AnsibleFileNotFound as e:
                raise AnsibleActionFail("could not find src=%s, %s" % (source, to_text(e)))
            b_tmp_source = to_bytes(tmp_source, errors='surrogate_or_strict')

            # template the source data locally & get ready to transfer
            try:
                with open(b_tmp_source, 'rb') as f:
                    try:
                        template_data = to_text(f.read(), errors='surrogate_or_strict')
                    except UnicodeError:
                        raise AnsibleActionFail("Template source files must be utf-8 encoded")

                # set jinja2 internal search path for includes
                searchpath = task_vars.get('ansible_search_path', [])
                searchpath.extend([self._loader._basedir, os.path.dirname(source)])

                # We want to search into the 'templates' subdir of each search path in
                # addition to our original search paths.
                newsearchpath = []
                for p in searchpath:
                    newsearchpath.append(os.path.join(p, 'templates'))
                    newsearchpath.append(p)
                searchpath = newsearchpath

                # add ansible 'template' vars
                temp_vars = task_vars.copy()
                # NOTE in the case of ANSIBLE_DEBUG=1 task_vars is VarsWithSources(MutableMapping)
                # so | operator cannot be used as it can be used only on dicts
                # https://peps.python.org/pep-0584/#what-about-mapping-and-mutablemapping
                temp_vars.update(generate_ansible_template_vars(constraints_src, source, dest))

                # force templar to use AnsibleEnvironment to prevent issues with native types
                # https://github.com/ansible/ansible/issues/46169
                templar = self._templar.copy_with_new_env(environment_class=AnsibleEnvironment,
                                                          searchpath=searchpath,
                                                          newline_sequence=newline_sequence,
                                                          available_variables=temp_vars)
                overrides = dict()
                resultant = templar.do_template(template_data, preserve_trailing_newlines=True, escape_backslashes=False, overrides=overrides)
            except AnsibleAction:
                raise
            except Exception as e:
                raise AnsibleActionFail("%s: %s" % (type(e).__name__, to_text(e)))
            finally:
                self._loader.cleanup_tmp_file(b_tmp_source)

            new_task = self._task.copy()
            local_tempdir = tempfile.mkdtemp(dir=C.DEFAULT_LOCAL_TMP)

            try:
                result_file = os.path.join(local_tempdir, os.path.basename(source))
                with open(to_bytes(result_file, errors='surrogate_or_strict'), 'wb') as f:
                    f.write(to_bytes(resultant, encoding=output_encoding, errors='surrogate_or_strict'))

                new_task.args.update(
                    dict(
                        src=result_file,
                        dest=dest
                    ),
                )
                del new_task.args['name']
                del new_task.args['virtualenv']
                del new_task.args['virtualenv_command']

                copy_action = self._shared_loader_obj.action_loader.get(
                    'copy',
                    task=new_task,
                    connection=self._connection,
                    play_context=self._play_context,
                    loader=self._loader,
                    templar=self._templar,
                    shared_loader_obj=self._shared_loader_obj
                )
                module_return.update(copy_action.run(task_vars=task_vars))
            finally:
                shutil.rmtree(to_bytes(local_tempdir, errors='surrogate_or_strict'))

        except AnsibleAction as e:
            module_return.update(e.result)
        finally:
            self._remove_tmp_path(self._connection._shell.tmpdir)

        return module_return

    def install_packages(self, packages, extra_args=None, module_args=None, task_vars=None):

        # We make a copy of module_args
        #
        module_args = self._task.args.copy()

        # Sanity checks
        #
        if not isinstance(packages, list):
            raise AnsibleActionFail("Packages not a list {s}".format(s=packages))
        if extra_args is not None:
            if not isinstance(extra_args, str):
                raise AnsibleActionFail("Extra args not a string {s}".format(s=extra_args))
        if not module_args.get('virtualenv_command'):
            raise AnsibleActionFail("virtualenv command was not set")

        module_args['name'] = packages
        if 'src' in module_args:
            del module_args['src']
        if extra_args is not None:
            module_args['extra_args'] = extra_args
        display.v(module_args['virtualenv_command'])
        ret = self._execute_module(module_name='pip', module_args=module_args, task_vars=task_vars)
        return ret

    def run(self, tmp=None, task_vars=None):

        self._supports_check_mode = True
        super(ActionModule, self).run(tmp, task_vars)

        # display.debug("Variables %s" % to_json(task_vars))

        # set virtualenv_command
        #
        self.set_virtualenv_command(task_vars=task_vars)

        # Get info about the targeted python interpreter
        ret0 = self.python_info(executable=self.get_python_executable(task_vars=task_vars), task_vars=task_vars)
        if ret0.get('failed'):
            raise AnsibleActionFail("Info about python interpreter has failed: {e}".format(e=ret0))
        ret0['item'] = 'python_info1'

        display.v("python_info1 %s" % to_json(ret0))
        display.v("Virtualenv %s" % to_json(self._task.args.get('virtualenv')))

        # create the virtualenv
        ret1 = self.install_packages(['wheel'], task_vars=task_vars)
        if ret1.get('failed'):
            raise AnsibleActionFail("Creation of virtualenv has failed: {e}".format(e=ret1))
        ret1['item'] = 'create_virtualenv'
        display.v("Create virtualenv %s" % to_json(ret1))

        packages = self._task.args.get('name')
        display.v("Packages %s" % to_json(packages))

        python_version = ret0['version']['majmin']
        display.v("Python version %s" % to_json(python_version))

        best_ansible_version = package_list(packages, python_version)
        display.v("Best ansible version %s" % to_json(best_ansible_version))

        # template constraints files
        #
        ret2 = {}
        if self._task.args.get('src'):
            ret2 = self.constraints(self._task.args.get('src'), task_vars=task_vars)
            ret2['item'] = "Template constraints file"
            if ret2.get('failed'):
                raise AnsibleActionFail("Template constraints file has failed: {e}".format(e=ret2))

        # Install workarounds for old ansible versions
        #
        ret4 = {}
        ret5 = {}
        if majmin(best_ansible_version) == '2.12' and python_version == '3.10':

            ret4 = self.install_packages(['cython<3.0.0'], task_vars=task_vars)
            if ret4.get('failed'):
                raise AnsibleActionFail("Install has failed: {e}".format(e=ret4))
            ret4['item'] = "Install cython"

            ret5 = self.install_packages(packages=['pyyaml'], extra_args="--no-build-isolation", task_vars=task_vars)
            if ret5.get('failed'):
                raise AnsibleActionFail("Install has failed: {e}".format(e=ret4))
            ret5['item'] = "Install pyyaml"

        # install the packages
        #
        ret3 = self.install_packages(packages, task_vars=task_vars)
        if ret3.get('failed'):
            raise AnsibleActionFail("Install has failed: {e}".format(e=ret3))
        ret3['item'] = 'Install_packages'

        module_return = {}
        module_return['ansible_version'] = best_ansible_version
        module_return['python_version'] = python_version
        module_return['packages'] = packages
        for ret in (ret0, ret1, ret2, ret3, ret4, ret5):
            if 'changed' in ret:
                if ret['changed']:
                    module_return['changed'] = True
                    break
        module_return['results'] = [ret0, ret1, ret2, ret3, ret4, ret5]
        return dict(module_return)
