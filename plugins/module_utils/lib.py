# Copyright (c) 2021 Markus Falb <markus.falb@mafalb.at>
# GNU General Public License v3.0+
# see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import shutil
import os
import sys


def which(executable):
    """Return absolute path"""
    if sys.version_info >= (3, 0):
        return shutil.which(executable)
    else:
        path = os.getenv('PATH')
        for p in path.split(os.pathsep):
            p = os.path.join(p, executable)
            if os.path.exists(p) and os.access(p, os.X_OK):
                return p
