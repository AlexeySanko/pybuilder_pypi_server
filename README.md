PyBuilder PyPi Server Plugin [![Build Status](https://travis-ci.org/AlexeySanko/pybuilder_pypi_server.svg?branch=master)](https://travis-ci.org/AlexeySanko/pybuilder_pypi_server)
=======================
Behaviour
---------
Setuptools and pip use different configs and into 
closed environment with own pypi servers it could bring
problems, because building project could get unexpected version 
(for example, from release repo instead of dev).
This plugin provide project property `pypi_server` 
for pypi repository name from .pipyrc file and uses
this property for assignment `distutils_upload_repository` 
and `install_dependencies_index_url` properties.
It guarantees that project will get dependencies 
and upload result to the same repository.

Project property could be passed from command line:
```
pyb clean analyze publish upload -P pypi_server=my_pypi
```

Or within initializers, but in this case any needed `PyBuilder` 
plugin  will be downloaded from default PyPi index. 
So command line usage is preferred way.

Note that `use_plugin` order is important in this case.
Any plugin before `use_plugin('pypi:pybuilder_pypi_server')` 
will be downloaded from default PyPi index. 

How to use
----------

Add plugin dependency to your `build.py`
```python
use_plugin('pypi:pybuilder_pypi_server')
```