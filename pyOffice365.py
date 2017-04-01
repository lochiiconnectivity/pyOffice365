# vim: ts=4:sw=4:sts=4:et

import simplejson as json
import re
import sys
import uuid

if sys.version_info >= (3, 0):
    import urllib.request as urllib2
    import urllib.parse as urllib
else:
    import urllib2
    import urllib

__version__ = '1.1.1'


class pyOffice365():

    __re_skiptoken = re.compile('.*\$skiptoken=([^&]*).*')
    __graph_api_endpoint = 'https://graph.windows.net'
    __graph_api_version = '1.5'
    __pcrest_api_endpoint = 'https://api.partnercenter.microsoft.com'
    __pcrest_api_version = 'v1'
    __oauth2_api_endpoint = 'https://login.windows.net'

    def __init__(self, debug_requests=False, debug_responses=False,
                 domain=None, appid=None, key=None, resource=None,
                 graph_api_endpoint=__graph_api_endpoint,
                 graph_api_version=__graph_api_version,
                 pcrest_api_endpoint=__pcrest_api_endpoint,
                 pcrest_api_version=__pcrest_api_version,
                 oauth_api_endpoint=__oauth2_api_endpoint):

        if not domain or not appid or not key:
            raise ValueError('Must provide domain, appid and key')

        self.__debug_requests = debug_requests
        self.__debug_responses = debug_responses
        self.__graph_api_endpoint = graph_api_endpoint
        self.__graph_api_version = graph_api_version
        self.__oauth2_api_endpoint = oauth_api_endpoint
        self.__domain = domain
        self.__appid = appid
        self.__key = key
        self.__resource = resource
        self.__access_token = None
        self.__pcrest_access_token = None
        self.__customer_token = None
        self.__ms_tracking_id = uuid.uuid4()

        if debug_requests:
            urllib2.install_opener(urllib2.build_opener(
                           urllib2.HTTPSHandler(debuglevel=1)))

    def graph_login(self):

        resource = self.__resource if self.__resource\
                    else self.__graph_api_endpoint

        postData = {
            "grant_type": "client_credentials",
            "resource": resource,
            "client_id": "%s@%s" % (self.__appid, self.__domain),
            "client_secret": self.__key,
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        req = urllib2.Request("%s/%s/oauth2/token?api-version=1.0" %
                              (self.__oauth2_api_endpoint, self.__domain),
                              urllib.urlencode(postData), headers)
        u = urllib2.urlopen(req)
        data = u.readlines()
        if self.__debug_responses is True:
            print(data)
        jdata = json.loads('\n'.join(data))
        if "access_token" in jdata:
            self.__access_token = jdata["access_token"]
        else:
            raise ValueError('Can not find access token, unable to log in')

    def get_access_token(self):
        return self.__access_token

    def get_pcrest_access_token(self):
        return self.__pcrest_access_token

    def pcrest_login(self):
        self.__pcrest_tenant_id = self.get_tenant()['value'][0]['objectId']

        req = urllib2.Request("%s/generatetoken" %
                              self.__pcrest_api_endpoint,
                              'grant_type=jwt_token',
                              headers=self.__auth_header__(
                               accept='application/json',
                               content_type='application/\
                               x-www-form-urlencoded'))
        u = urllib2.urlopen(req)
        data = u.readlines()
        if self.__debug_responses is True:
            print(data)
        jdata = json.loads('\n'.join(data))
        if "access_token" in jdata:
            self.__pcrest_access_token = jdata["access_token"]

    def __auth_header__(self, accept='application/json;odata=nometadata',
                        content_type='application/json;odata=nometadata',
                        authorization=None):
        if authorization is None:
            authorization = self.__access_token
        return {
            "Authorization": "Bearer %s" % (authorization),
            "Accept": accept,
            "Content-Type": content_type,
            "x-ms-correlation-id": uuid.uuid4(),
            "x-ms-tracking-id": self.__ms_tracking_id,
        }

    def __pcrest_auth_header__(self,
                               accept='application/json;odata=nometadata',
                               content_type='application/json;\
                                             odata=nometadata',
                               authorization=None, locale='en-US'):

        if authorization is None:
            authorization = self.__pcrest_access_token
        return {
            "Authorization": "Bearer %s" % (authorization),
            "Accept": accept,
            "Content-Type": content_type,
            "MS-RequestId": uuid.uuid4(),
            "MS-Contract-Version": "api-version: %s" %
            self.__pcrest_api_version,
            "MS-CorrelationId": uuid.uuid4(),
            "X-Locale": locale
        }

    def __doreq__(self, command, postdata=None, querydata={}, method=None):
        querydata['api-version'] = self.__graph_api_version

        if self.__access_token is None:
            self.graph_login()

        req = urllib2.Request("%s/%s/%s?%s" % (self.__graph_api_endpoint,
                              self.__domain, command,
                              urllib.urlencode(querydata)),
                              data=postdata, headers=self.__auth_header__())

        if method is not None:
            req.get_method = lambda: method

        try:
            u = urllib2.urlopen(req)
        except urllib2.HTTPError as e:
            data = e.readlines()
            if self.__debug_responses is True:
                print(data)
            try:
                jdata = json.loads('\n'.join(data))
            except:
                jdata = data
            return jdata

        data = u.readlines()
        if self.__debug_responses is True:
            print(data)

        try:
            jdata = json.loads('\n'.join(data))
        except:
            jdata = data
        return jdata

    def __pcrest_doreq__(self, command, postdata=None, querydata={},
                         method=None, token=None):
        if self.__pcrest_access_token is None:
            self.pcrest_login()

        req = urllib2.Request("%s/%s/%s?%s" % (self.__pcrest_api_endpoint,
                              self.__pcrest_api_version, command,
                              urllib.urlencode(querydata)), data=postdata,
                              headers=self.__pcrest_auth_header__(
                              authorization=token))

        if method is not None:
            req.get_method = lambda: method

        try:
            u = urllib2.urlopen(req)
        except urllib2.HTTPError as e:
            data = e.readlines()
            if self.__debug_responses is True:
                print(data)
            try:
                jdata = json.loads('\n'.join(data))
            except:
                jdata = data
            return jdata

        data = u.readlines()
        if self.__debug_responses is True:
            print(data)

        if "totalCount" in data[0]:
            jdata = json.loads(data[0])
        else:
            jdata = json.loads('\n'.join(data))

        return jdata

    def get_tenant(self):
        return self.__doreq__("tenantDetails")

    def get_customers(self):
        return self.__pcrest_doreq__("customers", querydata={'size': 950})

    def get_orders(self, tid=None):
        if tid is not None:
            return self.__pcrest_doreq__("customers/%s/orders" % tid)
        else:
            raise ValueError('get_orders requires tid')

    def get_subscription(self, tid=None, sid=None):
        if tid is not None and sid is not None:
            return self.__pcrest_doreq__("customers/%s/subscriptions/%s" %
                                         (tid, sid))
        else:
            raise ValueError('get_subscription requires tid and sid')

    def get_subscription_addons(self, tid=None, sid=None):
        if tid is not None and sid is not None:
            return self.__pcrest_doreq__(
                    "customers/%s/subscriptions/%s/addons" %
                    (tid, sid))
        else:
            raise ValueError('get_subscription_addons requires tid and sid')

    def update_subscription_quantity(self, tid=None, sid=None, quantity=0):

        if quantity < 1 or quantity > 9999:
            raise ValueError('update_subscription_quantity requires \
                quantity between 1 and 9999')

        if tid is not None and sid is not None:
            subscription = self.get_subscription(tid=tid, sid=sid)
            if subscription is not None:
                subscription["quantity"] = quantity
                res = self.__pcrest_doreq__("customers/%s/subscriptions/%s" %
                                            (tid, sid),
                                            postdata=json.dumps(subscription),
                                            method='PATCH')
                subscription = self.get_subscription(tid=tid, sid=sid)
                if subscription["quantity"] == quantity:
                    return res
                else:
                    raise ValueError('Unable to update quantity')
        else:
            raise ValueError('update_subscription_quantity \
                              requires tid and sid')

    def get_users(self, user=None):
        querydata = {}
        rdata = []

        if user:
            if '@' in user:
                users_path = "users/%s" % (user)
            else:
                users_path = "users/%s@%s" % (user, self.__domain)
        else:
            users_path = "users"

        while True:
            data = self.__doreq__(users_path, querydata=querydata)

            if 'userPrincipalName' in data:
                rdata += [data]
            elif 'value' in data:
                rdata += data["value"]
            if 'odata.nextLink' in data:
                skiptoken = self.__re_skiptoken.search(
                            data["odata.nextLink"]).group(1)
                querydata["$skiptoken"] = skiptoken
            else:
                break

        return rdata

    def get_skus(self):
        return self.__doreq__("subscribedSkus")

    def create_user(self, userdata):
        return self.__doreq__("users", postdata=json.dumps(userdata))

    def update_user(self, username, userdata):
        if '@' in username:
            return self.__doreq__("users/%s" %
                                  (username), postdata=json.dumps(userdata),
                                  method='PATCH')
        else:
            return self.__doreq__("users/%s@%s" % (username, self.__domain),
                                  postdata=json.dumps(userdata),
                                  method='PATCH')

    def assign_license(self, username, sku=None,
                       disabledplans=None, remove=None):

        # A single license sku can be added at a time
        add = [{"disabledPlans": disabledplans, "skuId": sku}] if sku else []

        # Either a single or multiple licenses can be removed at a time
        if remove:
            if type(remove) is str:
                remove = [remove]
            elif type(remove) is not list:
                raise ValueError("removal type must be string or list")
        else:
            remove = []

        postData = {"addLicenses": add, "removeLicenses": remove}

        if '@' in username:
            return self.__doreq__("users/%s/assignLicense" % (username),
                                  postdata=json.dumps(postData))
        else:
            return self.__doreq__("users/%s@%s/assignLicense" %
                                  (username, self.__domain),
                                  postdata=json.dumps(postData))
