# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pyOffice365',
    version='1.0.0',

    description='python module for managing an Office365 tenant via Graph API\
                 and Customer orders via Partner Center REST API',
    long_description=long_description,

    url='https://github.com/lochiiconnectivity/pyOffice365',

    author='Lochii Connectivity / cdfuow',
    author_email='lcreg-github@convergence.cx',

    license='Apache',

    classifiers=[
        'Development Status :: 5 - Production / Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='office365 microsoft graph rest pcrest',

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

)
