python module for managing an Office365 tenant via Graph API and Customer orders via Partner Center REST API

Updated to use version 0.9

Sample usage:

```python
import json
import pyOffice365

domain = "example.onmicrosoft.com"
appid = "<APPSERVICEPRINCIPAL GUID>"
key = "<APPSERVICEPRINCIPAL SYMMETRIC KEY>"

sku = "<PLAN SKU>"

o = pyOffice365.pyOffice365(domain)

o.login(appid, key)

results = o.get_users()
print json.dumps(results, sort_keys=True, indent=4, separators=(',', ': '))

newUser = {
	"accountEnabled": "true",
	"country": "Australia",
	"displayName": "example 1",
	"givenName": "example",
	"mailNickname": "example1",
	"passwordProfile": {
		"password": "can9r5gR40jJFFlL",
		"forceChangePasswordNextLogin": "false",
	},
	"surname": "one",
	"usageLocation": "AU",
	"userPrincipalName": "example1@example.onmicrosoft.com",
}

results = o.create_user(newUser)

print json.dumps(results, sort_keys=True, indent=4, separators=(',', ': '))

results = o.assign_license("example1", sku)

print json.dumps(results, sort_keys=True, indent=4, separators=(',', ': '))

```
[![Build Status](https://travis-ci.org/lochiiconnectivity/pyOffice365.svg?branch=master)](https://travis-ci.org/lochiiconnectivity/pyOffice365)

[![Coverage Status](https://coveralls.io/repos/github/lochiiconnectivity/pyOffice365/badge.svg?branch=master)](https://coveralls.io/github/lochiiconnectivity/pyOffice365?branch=master)
