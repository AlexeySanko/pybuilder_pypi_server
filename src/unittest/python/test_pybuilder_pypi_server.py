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
""" Tests for pybuilder_pypi_server"""
from os import remove
from os.path import (expanduser, isfile, join)
from setuptools.package_index import PyPIConfig

from pybuilder.core import Project
import pytest

from pybuilder_pypi_server import (
    init_pypi_server_plugin,
    reinitialize_pypi_server_plugin
)

PIPYRC_CONTENT = """
[distutils]
index-servers =
    {pypi1}
    {pypi2}

[{pypi1}]
repository: {url1}

[{pypi2}]
repository: {url2}
"""


@pytest.fixture(scope='function')
def from_pypirc(request):
    """ Read PyPi indexes info from existing ~/.pypirc file.
        Or crete temporary ~/.pypirc file with stub data."""
    pypirc_path = join(expanduser('~'), '.pypirc')
    is_pypirc_exists = True
    pipy_servers = []
    if isfile(pypirc_path):
        sections = PyPIConfig().sections()
        for section in sections:
            if section != 'distutils':
                pipy_servers.append(
                    (section, PyPIConfig().get(section, 'repository')))
        if not pipy_servers:
            raise ValueError("File ~/.pypirc is incorrect.")
        if len(pipy_servers) < 2:
            raise ValueError("File ~/.pypirc contains less than 2 servers.")
    else:
        is_pypirc_exists = False
        pypi_server1 = 'some_pypi'
        pypi_url1 = 'https://some/pypi/url'
        pypi_server2 = 'some_other_pypi'
        pypi_url2 = 'https://some/other/pypi/url'
        with open(pypirc_path, 'w') as file_out:
            file_out.write(PIPYRC_CONTENT.format(
                pypi1=pypi_server1, url1=pypi_url1,
                pypi2=pypi_server2, url2=pypi_url2))
        pipy_servers.append((pypi_server1, pypi_url1))
        pipy_servers.append((pypi_server2, pypi_url2))

    def teardown():  # pylint: disable=missing-docstring
        if not is_pypirc_exists:
            remove(pypirc_path)
    request.addfinalizer(teardown)
    return pipy_servers


def test_initialize_and_reinit_pypi_server_plugin(from_pypirc, mocker):  # pylint: disable=invalid-name,redefined-outer-name
    """ Check init_pypi_server_plugin function"""
    (pypi_server, pypi_url) = from_pypirc[0]
    project = Project("basedir")
    project.set_property('pypi_server', pypi_server)
    logger_mock = mocker.Mock()
    init_pypi_server_plugin(project, logger_mock)
    assert project.get_property('distutils_upload_repository') == pypi_server
    assert project.get_property('install_dependencies_index_url') == pypi_url
    logger_mock.info.assert_called_once_with(
        "Repository `%s` will be used to install_dependencies and "
        "distutils plugins." % pypi_server)
    # test re-init function
    (pypi_server, pypi_url) = from_pypirc[1]
    project.set_property('pypi_server', pypi_server)
    reinitialize_pypi_server_plugin(project, logger_mock)
    assert project.get_property('distutils_upload_repository') == pypi_server
    assert project.get_property('install_dependencies_index_url') == pypi_url
    logger_mock.warn.assert_called_once_with(
        "Property `pypi_server` defined on initialize stage. "
        "Please use command line `pyb ... -P pypi_server=...`, "
        "otherwise some packages could be downloaded "
        "from default PyPi index.")


def test_reinitialize_pypi_server_plugin(from_pypirc, mocker):  # pylint: disable=invalid-name,redefined-outer-name
    """ Check reinitialize_pypi_server_plugin function"""
    (pypi_server, pypi_url) = from_pypirc[0]
    project = Project("basedir")
    project.set_property('pypi_server', pypi_server)
    logger_mock = mocker.Mock()
    reinitialize_pypi_server_plugin(project, logger_mock)
    assert project.get_property('distutils_upload_repository') == pypi_server
    assert project.get_property('install_dependencies_index_url') == pypi_url
    logger_mock.warn.assert_called_once_with(
        "Property `pypi_server` defined on initialize stage. "
        "Please use command line `pyb ... -P pypi_server=...`, "
        "otherwise some packages could be downloaded "
        "from default PyPi index.")
    logger_mock.info.assert_called_once_with(
        "Repository `%s` will be used to install_dependencies and "
        "distutils plugins." % pypi_server)


def test_non_pypi_server_passed(mocker):  # pylint: disable=invalid-name
    """ Check init_pypi_server_plugin function"""
    project = Project("basedir")
    logger_mock = mocker.Mock()
    init_pypi_server_plugin(project, logger_mock)
    assert not logger_mock.info.called
    reinitialize_pypi_server_plugin(project, logger_mock)
    logger_mock.warn.assert_called_once_with(
        "No pypi server passed. "
        "Consider removing pypi_server plugin.")
