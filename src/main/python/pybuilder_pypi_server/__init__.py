#   -*- coding: utf-8 -*-
#
#   Copyright 2016 Alexey Sanko
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
import sys

from setuptools.package_index import PyPIConfig

from pybuilder.core import use_plugin
from pybuilder.reactor import Reactor

__author__ = 'Alexey Sanko'

use_plugin("python.core")


def initialize_pypi_server_plugin(project, logger):
    # workaround for command line properties
    # until https://github.com/pybuilder/pybuilder/pull/515
    if not project.get_property('pypi_server'):
        # try to get property from command line arguments
        for arg in sys.argv:
            if str(arg).startswith('pypi_server='):
                project.set_property('pypi_server',
                                     str(arg).replace('pypi_server=', ''))
                break
    if project.get_property('pypi_server'):
        logger.info("Repository `%s` will be used to "
                    "install_dependencies and distutils plugins." %
                    project.get_property('pypi_server'))
        project.set_property('distutils_upload_repository',
                             project.get_property('pypi_server'))
        pypi_url = PyPIConfig().get(
            project.get_property('pypi_server'), 'repository')
        project.set_property('install_dependencies_index_url', pypi_url)
    else:
        logger.warn("No pypi server passed. "
                    "Consider removing pypi_server plugin.")


initialize_pypi_server_plugin(Reactor.current_instance().project,
                              Reactor.current_instance().logger)
