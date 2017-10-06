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

from mock import Mock
from os import remove
from os.path import (
    expanduser,
    isfile,
    join
)
from setuptools.package_index import PyPIConfig

from pybuilder.core import Project

from pybuilder_pypi_server import (
    initialize_pypi_server_plugin
)


def get_first_nondistutils_section():
    sections = PyPIConfig().sections()
    for section in sections:
        if section != 'distutils':
            return section


def test_initialize_pypi_server_plugin():
    project = Project("basedir")
    pypirc_path = join(expanduser('~'), '.pypirc')
    is_pypirc_exists = True
    if isfile(pypirc_path):
        pypi_server = get_first_nondistutils_section()
        pypi_url = PyPIConfig().get(pypi_server, 'repository')
    else:
        is_pypirc_exists = False
        pypi_server = 'some_pypi'
        pypi_url = 'https://some/pypi/url'
        with open('pypirc_path', 'wb') as f:
            pipyrc_content = """
[distutils]
index-servers =
    %s

[some_pypi]
repository: %s
            """ % (pypi_server, pypi_url)
            f.write(pipyrc_content)
    project.set_property('pypi_server', pypi_server)
    initialize_pypi_server_plugin(project, Mock())
    assert project.get_property('distutils_upload_repository') == pypi_server
    assert project.get_property('install_dependencies_index_url') == pypi_url
    if not is_pypirc_exists:
        remove(pypirc_path)
