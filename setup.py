from setuptools import setup, find_packages

name = 'pyOffice365'
version = '1.0.0'

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

license = 'Apache'

classifiers = [
    'Development Status :: 5 - Production / Stable',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
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
