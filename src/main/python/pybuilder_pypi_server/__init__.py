#   -*- coding: utf-8 -*-
#
#   Copyright 2017 Alexey Sanko
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
""" PyBuilder plugin which provides possibility to centralize set
    all PyPi dependent properties"""
import sys

from setuptools.package_index import PyPIConfig

from pybuilder.core import before, use_plugin
from pybuilder.reactor import Reactor

from pybuilder_pypi_server import version

__author__ = 'Alexey Sanko'
__version__ = version.__version__

use_plugin("python.core")


def use_pypi_server_plugin(project, logger):
    """ Set PyPi dependent properties"""
    pypi_server = project.get_property('pypi_server')
    logger.info("Repository `%s` will be used to "
                "install_dependencies and distutils plugins." %
                pypi_server)
    project.set_property('distutils_upload_repository', pypi_server)
    pypi_url = PyPIConfig().get(pypi_server, 'repository')
    project.set_property('install_dependencies_index_url', pypi_url)
    project.set_property('pypi_server_on_import_plugin', pypi_server)


def init_pypi_server_plugin(project, logger):
    """ Init plugin on import stage (use_plugin).
        It allows to set properties before other plugins
        and download it from needed PyPi index"""
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
        use_pypi_server_plugin(project, logger)


init_pypi_server_plugin(
    Reactor.current_instance().project, Reactor.current_instance().logger)


@before("prepare", only_once=True)
def reinitialize_pypi_server_plugin(project, logger):
    """ Re-init properties if `pypi_server` was changed on initialization
        stage"""
    if project.get_property('pypi_server'):
        if (project.get_property('pypi_server') !=
                project.get_property('pypi_server_on_import_plugin')):
            logger.warn(
                "Property `pypi_server` defined on initialize stage. "
                "Please use command line `pyb ... -P pypi_server=...`, "
                "otherwise some packages could be downloaded "
                "from default PyPi index.")
            use_pypi_server_plugin(project, logger)
    else:
        logger.warn("No pypi server passed. "
                    "Consider removing pypi_server plugin.")
