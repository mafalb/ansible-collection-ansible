# Copyright (c) 2021 Markus Falb <markus.falb@mafalb.at>
# GNU General Public License v3.0+
# see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt

from __future__ import (absolute_import, division, print_function)
import yaml
__metaclass__ = type

datafile = open('roles/virtualenv/vars/data.yml', 'r')
data = yaml.load(datafile, Loader=yaml.FullLoader)
datafile.close()

data = data['mafalb_ansible_data']

if __name__ == '__main__':
    print(data)
