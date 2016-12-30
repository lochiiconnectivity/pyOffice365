.. _pyOffice365_guide:

pyOffice365 Guide
=================

Getting Started
----------------

pyOffice365 objects are instantiated by simply calling ``pyoffice365(domain=domain, appid=appid, key=key)``

Example:

.. code-block:: python

    import pyOffice365

    o = pyOffice365.pyOffice365(domain='test.onmicrosoft.com',
                                appid='545c2f9d-ffc8-4277-a2fc-828281f7e574',
                                key='c29tZSBzdHJpbmcgc29tZSBzdHJpbmcgc29tZSBzdHJpbmc=')


The credentials should be an application suitably authorized into your Azure Active Directory
with the permissions detailed in `<README.rst>`_ for the API and features you are trying to use.

Managing your Tenant with GRAPH features
========================================

Getting information about your tenant
-------------------------------------

Information about your tenant can be obtained with a call to ``get_tenant()``

Example:

.. code-block:: python

        o.get_tenant()

Results in a tenant object. An example can be seen at `<test_resources/tenant.json>`_. 


Getting a list of users
-----------------------

A list of users of your tenant can be obtained with a call to ``get_users(user=None)``

The user parameter is a string, and is optional and used to select a particular user. 

Ideally the user parameter should carry a fully qualified username (such as ``test@test.onmicrosoft.com``)
but should only the user part be passed to the parameter, the tenant domain will be appended to fully
qualify the username. 

Example:

.. code-block:: python

        o.get_users(user='john.smith')

Results in a user object. An example can be seen at `<test_resources/user.json>`_. 


Creating a user
---------------

Users are created by passing a user object to ``create_user(userdata)`` 
as the first positional parameter.

An example user object can be found at `<test_resources/user.json>`_.

The user object must contain the following minimum fields:

+--------------------+--------+--------------------------------------------------+ 
| Required Parameter | Type   | Description                                      |
+====================+========+==================================================+ 
| accountEnabled     | boolean| true if the account is enabled; otherwise, false.|
+--------------------+--------+--------------------------------------------------+ 
| displayName        | string | The name to display for the user.                |
+--------------------+--------+--------------------------------------------------+ 
| immutableId        | string | if federated user, take from metaverse (their AD)|
+--------------------+--------+--------------------------------------------------+ 
| mailNickname       | string | The mail alias for the user.                     |
+--------------------+--------+--------------------------------------------------+ 
| passwordProfile    | obj    | The password profile for the user.               |
+--------------------+--------+--------------------------------------------------+ 
| userPrincipalName  | string | UPN, must be a verified domain for the tenant    |
+--------------------+--------+--------------------------------------------------+ 

the *passwordProfile* object is comprised of the following :

+------------------------------+--------+--------------------------------------------------+ 
| Name                         | Type   | Notes                                            |
+==============================+========+==================================================+ 
| password                     | string | The password for the user.                       |
+------------------------------+--------+--------------------------------------------------+ 
| forceChangePasswordNextLogin | boolean| true if user must change password on login       |
+------------------------------+--------+--------------------------------------------------+ 

On success, the newly created user object is returned, else an error is thrown.

Example:

.. code-block:: python

        user = o.create_user({
                              'accountEnabled' : True,
                              'displayName' : 'John Smith',
                              'mailNickname': 'john.smith@foo.com',
                              'passwordProfile': { 'password' : 'foo1234', 'forceChangePasswordNextLogin' : True },
                              'userPrincipalName' : 'john.smith@test.onmicrosoft.com'
                             })

Updating a user
---------------

Users are updated by calling ``update_user(user, userdata)``. ``user`` is the first
positional parameter and is the ``objectId`` of the user you wish to update.
``userdata`` is the second positional parameter and represents a partial user object
containing only fields you wish to update.

On success, no response is returned. On failure, an error is thrown.

Example:

.. code-block:: python

        o.update_user('e1da4ed3-dd50-452f-889c-128add900c3d',
                      {
                        'department' : 'Sales',
                        'usageLocation' : 'US'
                      })

This will update both the department and usageLocation of the user ``John Smith``
otherwise known as objectId ``e1da4ed3-dd50-452f-889c-128add900c3d``

Getting available SKUs
----------------------

SKUs (available licenses) are obtained by calling ``get_skus()``

Example:

.. code-block:: python

        o.get_skus()

Results in a skus object. An example can be seen at `<test_resources/skus.json>`_.

(De)assigning Licenses to Users
-------------------------------

Licenses are (de)assigned to users by calling ``assign_license(user, sku=None, disabledplans=None, remove=None)``

``user`` is the first positional parameter and is the ``objectId`` of the user you wish to assign (or remove)
licenses from.

The ``sku`` parameter is the ``skuId`` of any SKU you wish to add to the user, whereas the ``remove`` 
parameter is the ``skuId`` of any SKU you wish to remove from the user.

the ``disabledplans`` parameter is a list of strings, containing ``servicePlanId`` (features) you wish to 
disable during the assignment of a SKU.

Example:

.. code-block:: python

        o.assign_license('e1da4ed3-dd50-452f-889c-128add900c3d',
                         sku='0764f96d-4604-459d-a3ea-dd7d7027fee9',
                         disabledPlans=['206b21a2-c0e5-48b9-ba2f-48fcfc38bfc5']
                        )

In this example, we assign the ``VISIOCLIENT`` SKU to ``John Smith`` but disable the use of the
``EXCHANGE_S_FOUNDATION`` feature.

On success, no response is returned. On failure, an error is thrown.

Managing your Customers with PCREST features
============================================

Getting a list of customers
---------------------------

Customers can be listed with a call to ``get_customers()``

Example:

.. code-block:: python

        o.get_customers()

Results in a customers object. An example can be seen at `<test_resources/customers.json>`_. 

Getting a list of orders for a customer
---------------------------------------

Orders (and therefore subscriptions) for a customer can be obtained
with a call to ``get_orders(tid=None)``

The ``tid`` parameter is mandatory and should be the ``tenantId`` of the customer's ``companyProfile`` object.

Example:

.. code-block:: python

        o.get_orders(tid='edce3354-c108-4b40-8b32-7f2faff06564`)

Results in an orders object. An example can be seen at `<test_resources/orders.json>`_. 

Getting a particular subscription for a customer
------------------------------------------------

Subscriptions (as seen in a customer's orders) can be obtained 
with a call to ``get_subscription(tid=None, sid=None)``

* The ``tid`` parameter is mandatory and should be the ``tenantId`` of the customer's ``companyProfile`` object.
* The ``sid`` parameter is mandatory and should be the ``subscriptionId`` of the customer's order ``lineItems`` list.

Example:

.. code-block:: python

        o.get_subscription(tid='edce3354-c108-4b40-8b32-7f2faff06564`,
                           sid='09155786-a2a0-46d6-8063-a44d07952018')

Results in a subscription object. An example can be seen at `<test_resources/subscription.json>`_. 

Getting subscription addons for a subscription
----------------------------------------------

Subscription addons (for example, disk space) can be obtained with a call to 
``get_subscription_addons(tid=None, sid=None)``

* The ``tid`` parameter is mandatory and should be the ``tenantId`` of the customer's ``companyProfile`` object.
* The ``sid`` parameter is mandatory and should be the ``subscriptionId`` of the customer's order ``lineItems`` list.

Example:

.. code-block:: python

        o.get_subscription_addons(tid='edce3354-c108-4b40-8b32-7f2faff06564`,
                                  sid='09155786-a2a0-46d6-8063-a44d07952018')

Results in a subscription addons object. An example can be seen at `<test_resources/subscription_addons.json>`_.

A subscription addons object is just another type of subscription and can be treated as such when modifying
quantities (where the ``id`` field will be called as a ``subscriptionId``). 

Updating subscription quantities
--------------------------------

Subscription quantities can be updated with a call to 
``update_subscription_quantity(tid=None, sid=None, quantity=0)``

* The ``tid`` parameter is mandatory and should be the ``tenantId`` of the customer's ``companyProfile`` object.
* The ``sid`` parameter is mandatory and should be the ``subscriptionId`` of the customer's order ``lineItems`` list.
* The ``quantity`` parameter is mandatory and must be an integer between 1 and 9999.

The ``quantity`` is the absolute new quantity of the subscription (or addons). It may not be zero.

Example:

.. code-block:: python

        o.update_subscription_quantity(tid='edce3354-c108-4b40-8b32-7f2faff06564`,
                                       sid='09155786-a2a0-46d6-8063-a44d07952018',
                                       quantity=2)

If successful an ``UpgradeResult`` message will be returned, indicating the new quantity. 

If not, an ``UpgradeError`` message will be returned, indicating in its ``Code`` and ``Description``
attributes the reason for not being able to update the subscription.

In some cases, a subscription ID can change, as part of a successful upgrade. 

The ``UpgradeResult`` message will carry both the original (As ``SourceSubscriptionId``) and
new subscription ID (as ``TargetSubscriptionID``) if this happens.


