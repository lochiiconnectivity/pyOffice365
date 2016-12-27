# vim: ts=4:sw=4:sts=4:et

import simplejson as json
import pyOffice365
import sys
from mock import MagicMock

if sys.version_info >= (3, 0):
    import urllib.request as urllib2
else:
    import urllib2

# Define Mock Response object


class FakeResponse(object):
    def __init__(self, body=None, headers=None):
        self.body = body
        self.headers = headers

    def readlines(self):
        return [json.dumps(self.body)]

# Define constant object


class const:
    class ConstError(TypeError):
        pass

    def __setattr__(self, name, value):
        if 'name' in self.__dict__:
            raise self.ConstError("Can't rebind const(%s)" % name)
        self.__dict__[name] = value

# Define constants

# Internal FakeResponse test
const.fake_url = 'http://fake.host'
const.fake_authorization = 'test_authorization'
const.fake_response = 'test_body'

# Initialiser
const.domain = 'test.onmicrosoft.com'
const.appid = 'test'
const.key = 'test'

# Login
const.login_pattern = 'oauth2/token'
const.access_token = 'test1234'

# PCRest Login
const.pcrest_login_pattern = 'generatetoken'
const.pcrest_access_token = 'test5678'

# Tenant
const.tenant_pattern = 'tenantDetails'
const.tenant_response = json.loads(open('test_resources/tenant.json',
                                   'r').read())
const.tenant_objid = 'f44b3eab-7135-4849-85fe-183919f17c9f'

# Customers
const.customers_pattern = 'customers'
const.customers_response = json.loads(open('test_resources/customers.json',
                                      'r').read())
const.customers_objid = 'edce3354-c108-4b40-8b32-7f2faff06564'

# Orders
const.orders_pattern = "customers/%s/orders" % const.customers_objid
const.orders_response = json.loads(open('test_resources/orders.json',
                                        'r').read())
const.orders_subscription_pos = 0
const.orders_subscription_id = '09155786-a2a0-46d6-8063-a44d07952018'
const.orders_subscription_qty = 2

# Subscriptions
const.subscription_pattern = "customers/%s/subscriptions/%s" %\
                              (const.customers_objid,
                               const.orders_subscription_id)
const.subscription_response = json.loads(open(
                                        'test_resources/subscription.json',
                                        'r').read())
const.subscription_offer_id = '2c6c3a47-5974-48df-908e-a229e14bcd88'

const.subscription_addons_pattern = "customers/%s/subscriptions/%s/addons" %\
                                     (const.customers_objid,
                                      const.orders_subscription_id)
const.subscription_addons_response = json.loads(open(
                                     'test_resources/subscription_addons.json',
                                     'r').read())

const.subscription_addon_id = '81b91bee-c71d-4964-98c8-9e33d93b7c47'

# Users
const.user = 'john.smith'

const.users_pattern = 'users'

const.users_user_pattern = "users/%s@%s" % (const.user, const.domain)

const.users_response = json.loads(open('test_resources/users.json',
                                       'r').read())

const.user_response = json.loads(open('test_resources/user.json',
                                      'r').read())

# SKUs

const.skus_pattern = 'subscribedSkus'

const.skus_response = json.loads(open('test_resources/skus.json',
                                      'r').read())

const.skus_consumedunits = 30

# Licenses

const.users_user_license_pattern = const.users_user_pattern + '/assignLicense'

# Define fake urlopen


def fake_urlopen(req):

    # Get auth string
    authorization = req.get_header('Authorization')
    if isinstance(authorization, str):
        if 'Bearer' in authorization:
            authorization = authorization[7:]

    # Get selector
    selector = None
    if sys.version_info >= (3, 0):
        selector = req.selector
    else:
        selector = req.get_selector()

    # Get method
    method = req.get_method()

    # Get data
    data = req.data

    # test login
    if const.login_pattern in selector:
        return FakeResponse(
                            body={'access_token': const.access_token}
                           )

    # Everything below requires us to be authenticated
    # Either with GRAPH or PCREST

    # GRAPH authenticated methods are below:
    if authorization == const.access_token:

        if const.pcrest_login_pattern in selector:
            return FakeResponse(
                                body={'access_token':
                                      const.pcrest_access_token}
                               )
        elif const.tenant_pattern in selector:
            return FakeResponse(body=const.tenant_response)
        elif method == 'POST' and const.users_pattern in selector:
            return FakeResponse(body=data)
        elif method == 'PATCH' and const.users_pattern in selector:
            return FakeResponse(body=data)
        elif method == 'PATCH' and\
                const.users_user_license_pattern in selector:
            return FakeResponse(body=const.user_response)
        elif const.users_user_pattern in selector:
            return FakeResponse(body=const.user_response)
        elif const.users_pattern in selector:
            return FakeResponse(body=const.users_response)
        elif const.skus_pattern in selector:
            return FakeResponse(body=const.skus_response)
        else:
            raise ValueError("Unknown selector for GRAPH")

    # PCREST authenticated methods are below
    elif authorization == const.pcrest_access_token:

        if const.orders_pattern in selector:
            return FakeResponse(body=const.orders_response)
        elif const.subscription_addons_pattern in selector:
            return FakeResponse(body=const.subscription_addons_response)
        elif method == 'PATCH' and const.subscription_pattern in selector:
            json_data = json.loads(data)
            subscription_response = const.subscription_response
            subscription_response['quantity'] = json_data['quantity']
            return FakeResponse(body=subscription_response)
        elif const.subscription_pattern in selector:
            return FakeResponse(body=const.subscription_response)
        elif const.customers_pattern in selector:
            return FakeResponse(body=const.customers_response)
        else:
            raise ValueError("Unknown selector for PCREST")
    # Fake internal response test
    elif authorization == const.fake_authorization:
        return FakeResponse(body=const.fake_response)
    # Unknown request handler
    else:
        raise ValueError("Incorrect access token")

# Patch urllib2 urlopen
urllib2.urlopen = MagicMock(side_effect=fake_urlopen)

# Get pyOffice365 object
o = pyOffice365.pyOffice365(domain=const.domain,
                            appid=const.appid, key=const.key)


# Start of tests

# (internal) test FakeResponse
def test_internal_fakeresponse():

    fake_request = urllib2.Request(const.fake_url)
    fake_request.add_header('authorization', const.fake_authorization)
    assert fake_urlopen(fake_request).readlines() == [ "\"%s\"" % const.fake_response ]


# Test login
def test_login():

    o.graph_login()

    assert o.get_access_token() == const.access_token


# Test PCREST login
def test_pcrest_login():

    o.pcrest_login()

    assert o.get_pcrest_access_token() == const.pcrest_access_token


# Test Get Tenant
def test_tenant():

    assert o.get_tenant()['value'][0]['objectId'] == const.tenant_objid


# Test Get Customers
def test_customers():

    assert o.get_customers()['items'][0]['id'] == const.customers_objid


# Test Get Orders
def test_orders():

    orders = o.get_orders(tid=const.customers_objid)
    lineitem = orders['items'][0]['lineItems'][const.orders_subscription_pos]

    assert lineitem['subscriptionId'] == const.orders_subscription_id
    assert lineitem['quantity'] == const.orders_subscription_qty


# Test Get Subscription
def test_subscription():

    subscription = o.get_subscription(tid=const.customers_objid,
                                      sid=const.orders_subscription_id)
    assert subscription['offerId'] == const.subscription_offer_id


# Test Get Subscription Addon
def test_subscription_addons():

    subscription_addons = o.get_subscription_addons(
                            tid=const.customers_objid,
                            sid=const.orders_subscription_id)
    assert subscription_addons['items'][0]['id'] == const.subscription_addon_id


# Test Updating subscription quantity
def test_subscription_update_qty():

    o.update_subscription_quantity(
                                    tid=const.customers_objid,
                                    sid=const.orders_subscription_id,
                                    quantity=3)


# Test listing users

def test_users():

    assert o.get_users()[1]['mailNickname'] == const.user
    assert o.get_users(user=const.user)[0]['mailNickname'] == const.user


# Test listing skus

def test_skus():

    assert o.get_skus()['value'][0]['consumedUnits'] ==\
           const.skus_consumedunits

# Test creating users


def test_create_user():

    response = json.loads(o.create_user(const.user_response))
    assert response['value'][0]['mailNickname'] == const.user


# Test updating users

def test_update_user():

    response = json.loads(o.update_user(const.user, const.user_response))
    assert response['value'][0]['mailNickname'] == const.user


# Test assigning licenses

def test_assign_license():

    response = json.loads(o.assign_license(const.user_response, remove='test'))
    assert response['removeLicenses'][0] == 'test'

