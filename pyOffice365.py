# vim: ts=4:sw=4:sts=4:et

import simplejson as json
import re
import types
import urllib
import urllib2
import uuid


class pyOffice365():

    __re_skiptoken = re.compile('.*\$skiptoken=([^&]*).*')
    __graph_api_endpoint = 'https://graph.windows.net'
    __graph_api_version = '1.5'
    ## TODO - REMOVE
    __crest_api_endpoint = 'https://api.cp.microsoft.com'
    ## TODO - REMOVE
    __crest_api_version = '2015-03-31'
    __pcrest_api_endpoint = 'https://api.partnercenter.microsoft.com'
    __pcrest_api_version = 'v1'
    __oauth2_api_endpoint = 'https://login.windows.net'

    def __init__(self, domain, debug_requests=False, debug_responses=False,
                 graph_api_endpoint=__graph_api_endpoint,
                 graph_api_version=__graph_api_version,
                 ## TODO - REMOVE
                 crest_api_endpoint=__crest_api_endpoint,
                 ## TODO - REMOVE
                 crest_api_version=__crest_api_version,
                 pcrest_api_endpoint=__pcrest_api_endpoint,
                 pcrest_api_version=__pcrest_api_version,
                 oauth_api_endpoint=__oauth2_api_endpoint):

        self.__debug_requests = debug_requests
        self.__debug_responses = debug_responses
        self.__graph_api_endpoint = graph_api_endpoint
        self.__graph_api_version = graph_api_version
        ## TODO - REMOVE
        self.__crest_api_endpoint = crest_api_endpoint
        ## TODO - REMOVE
        self.__crest_api_version = crest_api_version
        self.__oauth2_api_endpoint = oauth_api_endpoint
        self.__domain = domain
        self.__access_token = None
        ## TODO - REMOVE
        self.__crest_sa_token = None
        self.__pcrest_sa_token = None
        self.__customer_token = None
        ## TODO - REMOVE
        self.__crest_reseller_id = None
        ## TODO - REMOVE
        self.__crest_tenant_id = None
        self.__ms_tracking_id = uuid.uuid4()

        if debug_requests:
            urllib2.install_opener(urllib2.build_opener(urllib2.HTTPSHandler(debuglevel=1)))

    def graph_login(self, user, passwd, resource=None):
        if resource is None:
            resource = self.__graph_api_endpoint
        postData = {
            "grant_type": "client_credentials",
            "resource": resource,
            "client_id": "%s@%s" % (user, self.__domain),
            "client_secret": passwd,
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        req = urllib2.Request("%s/%s/oauth2/token?api-version=1.0" % (self.__oauth2_api_endpoint, self.__domain), urllib.urlencode(postData), headers)
        u = urllib2.urlopen(req)
        data = u.readlines()
        if self.__debug_responses is True:
            print data
        jdata = json.loads('\n'.join(data))
        if jdata.has_key("access_token"):
            self.__access_token =  jdata["access_token"]

    ## TODO - REMOVE
    def crest_login(self):
        self.__crest_tenant_id = self.get_tenant()['value'][0]['objectId']

        req = urllib2.Request("%s/my-org/tokens" % self.__crest_api_endpoint, 'grant_type=client_credentials', \
            headers=self.__auth_header__(accept='application/json', content_type='application/x-www-form-urlencoded'))
        u = urllib2.urlopen(req)
        data = u.readlines()
        if self.__debug_responses is True:
            print data
        jdata = json.loads('\n'.join(data))
        if jdata.has_key("access_token"):
            self.__crest_sa_token =  jdata["access_token"]

        req = urllib2.Request("%s/customers/get-by-identity?provider=AAD&type=tenant&tid=%s" % (self.__crest_api_endpoint, self.__crest_tenant_id) ,
            headers=self.__crest_auth_header__(accept='application/json'))
        u = urllib2.urlopen(req)
        data = u.readlines()
        if self.__debug_responses is True:
            print data
        jdata = json.loads('\n'.join(data))
        if jdata.has_key("id"):
            self.__crest_reseller_id =  jdata["id"]

    def pcrest_login(self):
        self.__pcrest_tenant_id = self.get_tenant()['value'][0]['objectId']

        req = urllib2.Request("%s/generatetoken" % self.__pcrest_api_endpoint, 'grant_type=jwt_token', \
            headers=self.__auth_header__(accept='application/json', content_type='application/x-www-form-urlencoded'))
        u = urllib2.urlopen(req)
        data = u.readlines()
        if self.__debug_responses is True:
            print data
        jdata = json.loads('\n'.join(data))
        if jdata.has_key("access_token"):
            self.__pcrest_access_token =  jdata["access_token"]

    def __auth_header__(self, accept='application/json;odata=nometadata', content_type='application/json;odata=nometadata', authorization=None):
        if authorization is None:
            authorization=self.__access_token
        return {
            "Authorization": "Bearer %s" % (authorization),
            "Accept": accept, 
            "Content-Type": content_type,
            "x-ms-correlation-id": uuid.uuid4(),
            "x-ms-tracking-id": self.__ms_tracking_id,
        }

    ## TODO - REMOVE
    def __crest_auth_header__(self, accept='application/json;odata=nometadata', content_type='application/json;odata=nometadata', authorization=None):
        if authorization is None:
            authorization=self.__crest_sa_token
        return {
            "Authorization": "Bearer %s" % (authorization),
            "Accept": accept, 
            "api-version" : self.__crest_api_version,
            "Content-Type": content_type,
            "x-ms-correlation-id": uuid.uuid4(),
            "x-ms-tracking-id": self.__ms_tracking_id,
        }

    def __pcrest_auth_header__(self,
                               accept='application/json;odata=nometadata',
                               content_type=\
                               'application/json;odata=nometadata',
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
        
        req = urllib2.Request("%s/%s/%s?%s" % (self.__graph_api_endpoint, self.__domain, command, urllib.urlencode(querydata)), data=postdata, headers=self.__auth_header__())

        if method is not None:
            req.get_method = lambda: method

        try:
            u = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            data = e.readlines()
            if self.__debug_responses is True:
                print data
            try:
                jdata = json.loads('\n'.join(data))
            except:
                jdata = data
            return jdata

        data = u.readlines()
        if self.__debug_responses is True:
            print data

        try:
            jdata = json.loads('\n'.join(data))
        except:
            jdata = data
        return jdata

    def __pcrest_doreq__(self, command, postdata=None, querydata={},
                         method=None, token=None):
        if self.__pcrest_sa_token is None:
            self.pcrest_login()

        req = urllib2.Request("%s/%s/%s?%s" % (self.__pcrest_api_endpoint,
                              self.__pcrest_api_version, command,
                              urllib.urlencode(querydata)), data=postdata,
                              headers=self.__pcrest_auth_header__\
                              (authorization=token))

        if method is not None:
            req.get_method = lambda: method

        try:
            u = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            data = e.readlines()
            if self.__debug_responses is True:
                print data
            try:
                jdata = json.loads('\n'.join(data))
            except:
                jdata = data
            return jdata

        data = u.readlines()
        if self.__debug_responses is True:
            print data

        if "totalCount" in data[0]:
            jdata = json.loads(data[0])
        else:
            jdata = json.loads('\n'.join(data))

        return jdata

    ## TODO - REMOVE
    def __crest_doreq__(self, command, postdata=None, querydata={}, method=None, resellerPath=True, token=None):
        if self.__crest_reseller_id is None:
            self.crest_login()

        req = None
        if resellerPath is True:
            req = urllib2.Request("%s/%s/%s?%s" % (self.__crest_api_endpoint, self.__crest_reseller_id, command, urllib.urlencode(querydata)), data=postdata, headers=self.__crest_auth_header__(authorization=token))
        else:
            req = urllib2.Request("%s/%s?%s" % (self.__crest_api_endpoint, command, urllib.urlencode(querydata)), data=postdata, headers=self.__crest_auth_header__(authorization=token))

        if method is not None:
            req.get_method = lambda: method

        try:
            u = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            data = e.readlines()
            if self.__debug_responses is True:
                print data
            try:
                jdata = json.loads('\n'.join(data))
            except:
                jdata = data
            return jdata

        data = u.readlines()
        if self.__debug_responses is True:
            print data
        try:
            jdata = json.loads('\n'.join(data))
        except:
            jdata = data
        return jdata

    ## TODO - REMOVE
    def __crest_get_customer__(self, tid=None):
        if self.__crest_tenant_id is None:
            self.crest_login()

        customer = self.__crest_doreq__("customers/get-by-identity", querydata={"provider": "AAD", "type": "external_group", "tid": tid, "etid": self.__crest_tenant_id}, resellerPath=False)

        if customer:
            req = urllib2.Request("%s/%s/tokens" % (self.__crest_api_endpoint, customer["id"]), 'grant_type=client_credentials', \
                headers=self.__auth_header__(accept='application/json', content_type='application/x-www-form-urlencoded'))
            u = urllib2.urlopen(req)
            data = u.readlines()
            if self.__debug_responses is True:
                print data
            jdata = json.loads('\n'.join(data))
            if jdata.has_key("access_token"):
                self.__customer_token = jdata["access_token"]
            
        return customer

    def get_tenant(self):
        return self.__doreq__("tenantDetails")

    def get_customers(self):
        return self.__pcrest_doreq__("customers", querydata={'size': 950})

    def get_orders(self, tid=None):
        if tid is not None:
            return self.__pcrest_doreq__("customers/%s/orders" % tid)

    ## TODO - REMOVE
    def get_contracts(self):
        return self.__doreq__("contracts")

    ## TODO - REMOVE
    def get_crest_subscriptions(self, tid=None):

        querydata = {}
        rdata = []

        customer = self.__crest_get_customer__(tid=tid)

        if customer:
            subscriptions_path = "subscriptions"
            querydata = {"recipient_customer_id": customer["id"]}
            while True:
                data = self.__crest_doreq__(subscriptions_path, querydata=querydata, token=None)
                if type(data) != types.DictType:
                    return None
                if 'items' in data:
                    rdata += [data]
                if 'odata.nextLink' in data:
                    skiptoken = self.__re_skiptoken.search(data["odata.nextLink"]).group(1)
                    querydata["$skiptoken"] = skiptoken
                else:
                    break

        return rdata

    ## TODO - REMOVE
    def get_crest_orders(self, tid=None):

        querydata = {}
        rdata = []

        customer = self.__crest_get_customer__(tid=tid)
    
        if customer:
            orders_path = "orders"
            querydata = {"recipient_customer_id": customer["id"]}
            while True:
                data = self.__crest_doreq__(orders_path, querydata=querydata, token=None)
                if type(data) != types.DictType:
                    return None
                if 'items' in data:
                    rdata += [data]
                if 'odata.nextLink' in data:
                    skiptoken = self.__re_skiptoken.search(data["odata.nextLink"]).group(1)
                    querydata["$skiptoken"] = skiptoken
                else:
                    break

        return rdata
        
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
            if type(data) != types.DictType:
                return None
            if 'userPrincipalName' in data:
                rdata += [data]
            elif 'value' in data:
                rdata += data["value"]
            if 'odata.nextLink' in data:
                skiptoken = self.__re_skiptoken.search(data["odata.nextLink"]).group(1)
                querydata["$skiptoken"] = skiptoken
            else:
                break

        return rdata

    def get_metadata(self):
        return self.__doreq__("$metadata")

    def get_skus(self):
        return self.__doreq__("subscribedSkus")

    def create_user(self, userdata):
        return self.__doreq__("users", json.dumps(userdata))

    def update_user(self, username, userdata):
        if '@' in username:
            return self.__doreq__("users/%s" % (username), postdata=json.dumps(userdata), method='PATCH')
        else:
            return self.__doreq__("users/%s@%s" % (username, self.__domain), postdata=json.dumps(userdata), method='PATCH')

    def assign_license(self, username, sku=None, disabledplans=None, remove=None):
        add = [{ "disabledPlans": disabledplans, "skuId": sku }] if sku else []
        remove = [remove] if remove else []
        postData = { "addLicenses": add, "removeLicenses": remove }

        if '@' in username:
            return self.__doreq__("users/%s/assignLicense" % (username), postdata=json.dumps(postData))
        else:
            return self.__doreq__("users/%s@%s/assignLicense" % (username, self.__domain), postdata=json.dumps(postData))
