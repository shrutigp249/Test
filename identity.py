#(C) Copyright 2019 Hewlett Packard Enterprise Development LP.
import requests
import paramiko
import logging
import os


class OSClient:

    URI_OIDCCLIENT = "/oauth2/"
    URI_PROVIDERS = "/providers/"
    URI_PROVIDERTYPES = "/provider-types"
    URI_SCIM = "/scim/"

    HEADERS = {'Content-Type': 'application/x-www-form-urlencoded'}
    POST_HEADERS = {'Content-Type': 'application/json'} 
    SCIM_HEADERS = {'Content-Type': 'application/scim+json'}

    def __init__(self, host_url, client_id, username, password):
        self.host_url = host_url
        self.rest_prefix = host_url + "/identity"
        self.grant_type = "password"
        self.client_id = client_id
        self.username = username
        self.password = password
        self.scope = "openid email profile"
        self.connect()

    def __del__(self):
        self.disconnect()

    def connect(self):
        full_url = self.host_url + "/auth/realms/master/protocol/openid-connect/token"
        data = {'grant_type': self.grant_type,'client_id': self.client_id,'username': self.username,'password': self.password,'scope': self.scope}
        r = requests.post(full_url, data = data )
        r_json = r.json()
        # If there's an error, raise an exception
        r.raise_for_status()
        self.token = r_json["id_token"]
        OSClient.HEADERS["Authorization"] = r_json["id_token"]
        OSClient.POST_HEADERS["Authorization"] = r_json["id_token"]
        OSClient.SCIM_HEADERS["Authorization"] = r_json["id_token"]

    def disconnect(self):
        full_url = self.rest_prefix
        return requests.delete(full_url, headers=OSClient.HEADERS)

    def resp_logging(self, expected_status, recevied_response):
        get_return_code = {
            101: "Switching Protocols",
            200: "OK",
            201: "Created",
            202: "Accepted",
            203: "Non-Authoritative Information",
            204: "No Content",
            205: "Reset Content",
            206: "Partial Content",
            300: "Multiple Choices",
            301: "Moved Permanently",
            302: "Moved Temporarily",
            303: "See Other",
            304: "Not Modified",
            305: "Use Proxy",
            400: "Bad Request",
            401: "Unauthorized",
            402: "Payment Required",
            403: "Forbidden",
            404: "Not Found",
            405: "Method Not Allowed",
            406: "None Acceptable",
            407: "Proxy Authentication Required",
            408: "Request Timeout",
            409: "Conflict",
            410: "Gone",
            411: "Length Required",
            412: "Unless True",
            415: "Unsupported Media Type",
            500: "Internal Server Error",
            501: "Not Implemented",
            502: "Bad Gateway",
            503: "Service Unavailable",
            504: "Gateway Timeout",
            }
        try:
            received_response_msg = get_return_code[recevied_response.status_code]
        except KeyError:
            received_response_msg = "Unexpected/Unknown response"
        msg = "\n" + ( 'Expected status is {} : {}' .format(
                expected_status, get_return_code[expected_status]))
        msg = msg + "\n" + ('But Received status is {} : {}'.format(
                recevied_response.status_code, received_response_msg))
        msg = msg + "\n" +  ('Received response for the failure is : {}'.format(
                    recevied_response.content))
        msg = msg + "\n" +  ('Onesphere URL is : {}'.format(
                    recevied_response.url))
        msg = msg + "\n" +  ('Onesphere Request method is : {}'.format(
                    recevied_response.request.method))
        msg = msg + "\n" +  ('Time stamp from response header is/ : {}'.format(
                    recevied_response.headers['Date']))
        assert expected_status == recevied_response.status_code, msg

    def register_idpTypeRequest(self, data):
        """method to create register IDP type request
        @:param: data-idp name
        @:return: returns the response of POST API request
        """
        full_url = self.rest_prefix + OSClient.URI_PROVIDERTYPES
        data = {
		"name": data['name'],
       	"resourceTypes": [
       		{
       			"name":"users",
       			"path": "/principals/users"
       		},
       		{
       			"name":"groups",
       			"path": "/principals/groups"
       		}
       		]
			}
        return requests.post(full_url, headers=OSClient.HEADERS, json=data)

    def list_idpTypesRequest(self, idp_name=None):
        """method to fetch identity provider Types
        @:return: returns the response of GET API request
        """
        if idp_name:
            full_url = self.rest_prefix + OSClient.URI_PROVIDERTYPES + idp_name
        else:
	    full_url = self.rest_prefix + OSClient.URI_PROVIDERTYPES
        return requests.get(full_url, headers=OSClient.HEADERS)
	
    def delete_idpTypes(self, idp_name=None):
        """method to delete identity provider Types
        @:return: returns the response of delete API request
        """
        full_url = self.rest_prefix + OSClient.URI_PROVIDERTYPES + idp_name
        return requests.get(full_url, headers=OSClient.HEADERS,params=params)

    def list_principals(self, idp_name):
        """method to list principals supported by identity provider Types
        @:return: returns the response of GET API request
        """
        full_url = self.rest_prefix + OSClient.URI_PROVIDERTYPES + "/" + idp_name + "/principal-types"
        return requests.get(full_url, headers=OSClient.HEADERS)

    def register_idp(self,  tenant_id, idp_name, provider_Type, apiKey, authUrl):
        """method to create register oidc client
        @:param: idp_name, providerType, apikey, authUrl
        @:return: returns the response of POST API request
        """
        full_url = self.rest_prefix + OSClient.URI_PROVIDERS + tenant_id
        data = {"name": idp_name,
                "providerType": provider_Type,
				"apiKey": apiKey,
				"authUrl": authUrl
               }
        return requests.post(full_url, headers=OSClient.POST_HEADERS, json=data)
        	
    def list_idps(self,tenant_id):
        """method to fetch identity providers
        @:return: returns the response of GET API request
        """
        full_url = self.rest_prefix + OSClient.URI_PROVIDERS + tenant_id
        return requests.get(full_url, headers=OSClient.HEADERS)
	
    def list_users(self,tenant_id,user_id=None):
	"""method to list users
        @:return: returns the response of GET API request
        """
        if user_id:
	   full_url = self.rest_prefix + OSClient.URI_PROVIDERS + tenant_id + "/1/principals/users/" + user_id
        else:
           full_url = self.rest_prefix + OSClient.URI_PROVIDERS + tenant_id + "/1/principals/users"
        params = {"tenant_id":tenant_id,"user_id": user_id }
        return requests.get(full_url, headers=OSClient.HEADERS,params=params)
		
    def list_groups(self, tenant_id,group_id=None):
        """method to list groups
        @:return: returns the response of GET API request
        """
        if group_id:
           full_url = self.rest_prefix + OSClient.URI_PROVIDERS + tenant_id + "/1/principals/groups/" + group_id
        else:
           full_url = self.rest_prefix + OSClient.URI_PROVIDERS + tenant_id + "/1/principals/groups"
        params = {"tenant_id":tenant_id,"group_id": group_id }
        return requests.get(full_url, headers=OSClient.HEADERS,params=params)
	
    def list_local_users(self, tenant_id):
        """method to list users(according to SCIM spec 2.0)
        @:return: returns the response of GET API request
        """

        full_url = self.rest_prefix + OSClient.URI_SCIM + tenant_id + "/Users" 
        return requests.get(full_url, headers=OSClient.HEADERS)
		
    def create_local_user(self, data, tenant_id):
        """method creates local user
        @:param: data: input parameters to create user
        @:return: returns the response of POST API request
        """
        full_url = self.rest_prefix + OSClient.URI_SCIM + tenant_id +"/Users"
        payload = {
            "displayName": data['displayName'],
            "userName": data['userName'],
			"password": data['password'],
                        "familyName": data['name']['familyName'],
                        "givenName": data['name']['givenName'],
                        "active": True
        }
        return requests.post(full_url, headers=OSClient.SCIM_HEADERS, json=payload)
		
    def delete_local_user(self, tenant_id, user_id):
        """method to delete user
        @:param: tenant_id, user_id
        @:return: return the response of DELETE API request
        """
        full_url = self.rest_prefix + OSClient.URI_SCIM +  tenant_id +"/Users/" + user_id
        return requests.delete(full_url, headers=OSClient.SCIM_HEADERS)

    def register_oidcClient(self,  tenant, name, id, secret, redirect_uris):
        """method to create register oidc client
        @:param: name: app name
        @:param: id: app id
        @:param: secret
        @:param: redirect uris
        @:return: returns the response of POST API request
        """
        full_url = self.rest_prefix + OSClient.URI_OIDCCLIENT + tenant + "/client"
        data = {"name": name,
                "id": id,
				"secret": secret,
				"redirect_uris": redirect_uris
               }
        return requests.post(full_url, headers=OSClient.HEADERS, json=data)
	
    def delete_oidcClient(self, tenant, id):
        """method to delete oidcClient
        @:param: id : oidcClient id
        @:param: tenant
        @:return: return the response of DELETE API request
        """
        full_url = self.rest_prefix + OSClient.URI_OIDCCLIENT + tenant + "/client"+ "/" + id
        return requests.delete(full_url, headers=OSClient.HEADERS)
		
    def update_oidcClient(self, tenant, id, data):
        """method updates oidc client
        @:param: data: input parameters(name, redirect_uris) to update client
        @:return: returns the response of PUT API request
        """
        full_url = self.rest_prefix + OSClient.URI_OIDCCLIENT + tenant + "/client/" + id
        payload = {
            "name": data['name'],
            "redirect_uris": data['redirect_uris']
        }
        return requests.post(full_url, headers=OSClient.HEADERS, json=payload)

