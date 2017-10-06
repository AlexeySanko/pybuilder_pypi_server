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

from setuptools.package_index import PyPIConfig

from pybuilder.core import init, use_plugin

__author__ = 'Alexey Sanko'

use_plugin("python.core")


@init
def initialize_pypi_server_plugin(project, logger):
    if project.get_property('pypi_server'):
        logger.info("""Repository `%s` will be used to install_dependencies and distutils plugins.""")
        project.plugin_depends_on('setuptools')
        project.set_property('distutils_upload_repository', project.get_property('pypi_server'))
        pypi_url = PyPIConfig().get(project.get_property('pypi_server'), 'repository')
        project.set_property('install_dependencies_index_url', pypi_url)
    else:
        logger.warn("No pypi server passed. Consider removing pypi_server plugin.")
