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

    def install_packages(self, packages, extra_args=None, task_vars=None):

        # Sanity checks
        #
        if not isinstance(packages, list):
            raise AnsibleActionFail("Packages not a list {s}".format(s=packages))
        if extra_args is not None:
            if not isinstance(extra_args, str):
                raise AnsibleActionFail("Extra args not a string {s}".format(s=extra_args))

        module_args = self._task.args.copy()
        module_args['name'] = packages
        del module_args['src']
        if extra_args is not None:
            module_args['extra_args'] = extra_args
        ret = self._execute_module(module_name='pip', module_args=module_args, task_vars=task_vars)
        return ret

    def run(self, tmp=None, task_vars=None):

        self._supports_check_mode = True
        super(ActionModule, self).run(tmp, task_vars)
        module_args = self._task.args.copy()

        # display.debug("Variables %s" % to_json(task_vars))

        ansible_python_executable = task_vars.get('ansible_python')['executable']
        if 'src' in module_args:
            constraints_src = module_args["src"]

            # pip module is crashing if this is present
            #
            del module_args["src"]

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

        best_ansible_version = package_list(packages, python_version)
        display.v("Best ansible version %s" % to_json(best_ansible_version))

        # template constraints files
        #
        ret2 = {}
        if 'constraints_src' in locals():
            ret2 = self.constraints(constraints_src, task_vars=task_vars)
            ret2['item'] = "Template constraints file"
            if 'failed' in ret2 and ret2['failed']:
                raise AnsibleActionFail("Template constraints file has failed: {e}".format(e=ret2))
            ret2['failed'] = False

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
        ret3 = self._execute_module(module_name='pip', module_args=module_args, task_vars=task_vars)
        ret3['item'] = 'install_packages'
        if 'failed' not in ret3:
            ret3['failed'] = False

        module_return = {}
        module_return['failed'] = ret3['failed']
        module_return['ansible_version'] = best_ansible_version
        module_return['python_version'] = python_version
        module_return['packages'] = packages
        for ret in (ret0, ret1, ret2, ret3):
            if 'changed' in ret:
                if ret['changed']:
                    module_return['changed'] = True
                    break
        module_return['results'] = [ret0, ret1, ret2, ret3, ret4, ret5]
        return dict(module_return)
