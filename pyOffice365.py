# vim: ts=4:sw=4:sts=4:et

import json
import re
import types
import urllib
import urllib2
import uuid

class pyOffice365():

    __re_skiptoken = re.compile('.*\$skiptoken=([^&]*).*')

    def __init__(self, domain, debug=False, apiversion='1.5'):
        self.debug = debug
        self.domain = domain
        self.__access_token = None
        self.__crest_sa_token = None
        self.__crest_reseller_id = None
        self.__ms_tracking_id = uuid.uuid4()
        self.apiversion = apiversion
        if debug:
            urllib2.install_opener(urllib2.build_opener(urllib2.HTTPSHandler(debuglevel=1)))

    def login(self, user, passwd):
        postData = {
            "grant_type": "client_credentials",
            "resource": "https://graph.windows.net",
            "client_id": "%s@%s" % (user, self.domain),
            "client_secret": passwd,
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        req = urllib2.Request("https://login.windows.net/%s/oauth2/token?api-version=1.0" % (self.domain), urllib.urlencode(postData), headers)
        u = urllib2.urlopen(req)
        data = u.readlines()
        jdata = json.loads('\n'.join(data))
        if jdata.has_key("access_token"):
            self.__access_token =  jdata["access_token"]

    def crest_login(self):
        tenant_id = self.get_tenant()['value'][0]['objectId']

        req = urllib2.Request("https://api.cp.microsoft.com/my-org/tokens", 'grant_type=client_credentials', \
            headers=self.__auth_header__(accept='application/json', content_type='application/x-www-form-urlencoded'))
        u = urllib2.urlopen(req)
        data = u.readlines()
        jdata = json.loads('\n'.join(data))
        if jdata.has_key("access_token"):
            self.__crest_sa_token =  jdata["access_token"]

        req = urllib2.Request("https://api.cp.microsoft.com/customers/get-by-identity?provider=AAD&type=tenant&tid=%s" % tenant_id, \
            headers=self.__crest_auth_header__(accept='application/json'))
        u = urllib2.urlopen(req)
        data = u.readlines()
        jdata = json.loads('\n'.join(data))
        if jdata.has_key("id"):
            self.__crest_reseller_id =  jdata["id"]


    def __auth_header__(self, accept='application/json;odata=nometadata', content_type='application/json;odata=nometadata'):
        return {
            "Authorization": "Bearer %s" % (self.__access_token),
            "Accept": accept, 
            "Content-Type": content_type,
            "x-ms-correlation-id": uuid.uuid4(),
            "x-ms-tracking-id": self.__ms_tracking_id,
        }

    def __crest_auth_header__(self, accept='application/json;odata=nometadata', content_type='application/json;odata=nometadata'):
        return {
            "Authorization": "Bearer %s" % (self.__crest_sa_token),
            "Accept": accept, 
            "api-version" : "2015-03-31",
            "Content-Type": content_type,
            "x-ms-correlation-id": uuid.uuid4(),
            "x-ms-tracking-id": self.__ms_tracking_id,
        }

    def __doreq__(self, command, postdata=None, querydata={}, method=None):
        querydata['api-version'] = self.apiversion
        
        req = urllib2.Request("https://%s/%s/%s?%s" % ('graph.windows.net', self.domain, command, urllib.urlencode(querydata)), data=postdata, headers=self.__auth_header__())

        if method is not None:
            req.get_method = lambda: method

        try:
            u = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            data = e.readlines()
            try:
                jdata = json.loads('\n'.join(data))
            except:
                jdata = data
            return jdata

        data = u.readlines()
        try:
            jdata = json.loads('\n'.join(data))
        except:
            jdata = data
        return jdata

    def __crest_doreq__(self, command, postdata=None, querydata={}, method=None):
        if self.__crest_reseller_id is None:
            self.crest_login()

        req = urllib2.Request("https://%s/%s/%s?%s" % ('api.cp.microsoft.com', self.__crest_reseller_id, command, urllib.urlencode(querydata)), data=postdata, headers=self.__crest_auth_header__())

        if method is not None:
            req.get_method = lambda: method

        try:
            u = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            data = e.readlines()
            try:
                jdata = json.loads('\n'.join(data))
            except:
                jdata = data
            return jdata

        data = u.readlines()
        try:
            jdata = json.loads('\n'.join(data))
        except:
            jdata = data
        return jdata

    def get_tenant(self):
        return self.__doreq__("tenantDetails")

    def get_contracts(self):
        return self.__doreq__("contracts")

    def get_users(self):
        querydata = {}
        rdata = []

        while True:
            data = self.__doreq__("users", querydata=querydata)
            if type(data) != types.DictType:
                print data
                return None
            if 'value' in data:
                rdata += data["value"]
            if data.has_key("odata.nextLink"):
                skiptoken = self.__re_skiptoken.search(data["odata.nextLink"]).group(1)
                querydata["$skiptoken"] = skiptoken
            else:
                break

        return rdata

    def get_metadata(self):
        return self.__doreq__("$metadata")

    def get_skus(self):
        return self.__doreq__("subscribedSkus")

    def get_user(self, username):
        return self.__doreq__("users/%s@%s" % (username, self.domain))
    
    def create_user(self, userdata):
        return self.__doreq__("users", json.dumps(userdata))

    def update_user(self, username, userdata):
        return self.__doreq__("users/%s@%s" % (username, self.domain), postdata=json.dumps(userdata), method='PATCH')

    def assign_license(self, username, sku, remove = None):
        postData = {
            "addLicenses": [
                {
                    "disabledPlans": [],
                    "skuId": sku,
                }
            ],
            "removeLicenses": remove,
        }

        return self.__doreq__("users/%s@%s/assignLicense" % (username, self.domain), postdata=json.dumps(postData))
