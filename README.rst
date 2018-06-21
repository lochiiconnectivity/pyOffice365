.. image:: https://travis-ci.org/lochiiconnectivity/pyOffice365.svg?branch=master
       :target: https://travis-ci.org/lochiiconnectivity/pyOffice365

.. image:: https://coveralls.io/repos/github/lochiiconnectivity/pyOffice365/badge.svg?branch=master
   :target: https://coveralls.io/github/lochiiconnectivity/pyOffice365?branch=master

.. image:: https://pyup.io/repos/github/lochiiconnectivity/pyOffice365/shield.svg
   :target: https://pyup.io

.. image:: https://pyup.io/repos/github/lochiiconnectivity/pyOffice365/python-3-shield.svg
   :target: https://pyup.io

.. _pyOffice365:

pyOffice365
===========

Overview
--------

pyOffice365 provides a framework for both:

* Managing users and licenses inside an Office365 Tenant (GRAPH API)

* Managing customers, subscription orders and addons as an Office365 reseller (PCREST API)

You need not be a reseller to take advantage of the user and license management
this libarary affords you.

pyOffice365 requires Python 2.7, 3.4, or 3.5.

Installing from source
----------------------

pyOffice365 can be installed from source like such:

.. code-block:: bash

  $ (sudo) python setup.py install

Preparing your Office365 environment
------------------------------------

To prepare for use of the GRAPH API, that is management of users 
and licenses within your tenant, you should create an API/Web application
with the following permissions:

* Windows Azure Active Directory - Read and write directory data
* Windows Azure Active Directory - Read all hidden memberships
* Microsoft Graph - Read and write directory data
* Microsoft Graph - Read all hidden memberships

Record the tenant domain, application ID (sometimes called client ID) and
key you generate for use with pyOffice365

Preparing your reseller environment
------------------------------------

To prepare for use of the PCREST API, that is the management of customers
and orders through Partner Center, you should create an API/Web application
with the default set of permissions.

Record the tenant domain, application ID (sometimes called client ID) and
key you generate for use with pyOffice365

Quickstart
----------

.. code-block:: python

    import pyOffice365

    o = pyOffice365.pyOffice365(domain='test.onmicrosoft.com',
                                appid='545c2f9d-ffc8-4277-a2fc-828281f7e574',
                                key='c29tZSBzdHJpbmcgc29tZSBzdHJpbmcgc29tZSBzdHJpbmc=')

    print o.get_users()


Documentation
-------------

API Documentation can be found in `<GUIDE.rst>`_

Support / Reporting Bugs / Development Versions
-----------------------------------------------

Visit `<http://github.com/lochiiconnectivity/pyOffice365/>`_ to download development or tagged
versions.

Visit `<http://github.com/lochiiconnectivity/pyOffice365/issues/>`_ to report bugs.
