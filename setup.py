import io
import os
import re
from setuptools import setup, find_packages

# Functions for reading version out of package file, which maintains it


def read(*names, **kwargs):
    with io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf8")
    ) as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


# Setup variables

name = 'pyOffice365'
package_file = 'pyOffice365.py'
version = find_version(package_file)

description = 'python module for managing Office365'

long_description = 'python module for managing an Office365 tenant via\
                    Graph API and Customer orders via Partner Center\
                    REST API'

url = 'https://github.com/lochiiconnectivity/pyOffice365'

author = 'Lochii Connectivity / cdfuow'
author_email = 'lcreg-github@convergence.cx'

setup_requires= [
    'pytest-runner',
],

install_requires = [
    'setuptools>=31.0.0',
    'six>=1.9',
    'simplejson',
]

tests_require = [
    'pytest',
    'pytest-cov',
    'mock',
]

license = 'Unknown'

classifiers = [
    'Development Status :: 5 - Production / Stable',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'License :: Unknown',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
]

keywords = 'office365 microsoft graph rest pcrest'

packages = find_packages(exclude=['contrib', 'docs', 'tests'])

setup(
    name=name,
    version=version,
    description=description,
    long_description=long_description,
    url=url,
    author=author,
    author_email=author_email,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    license=license,
    classifiers=classifiers,
    keywords=keywords,
    packages=packages
)
