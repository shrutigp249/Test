# (C) Copyright 2017-2019 Hewlett Packard Enterprise Development LP

import requests
import unittest
import json
import os
import random
import string

from identity import OSClient

tenant_id = os.environ['tenant_id']

class IDENTITY_Test:

        @classmethod
        def setUpClass(cls):
           super(IDENTITY_Test, cls).setUpClass()
           host_url = os.environ['host_url']
           username = os.environ['username']
           password = os.environ['password']
           client_id = os.environ['client_id']
           cls.identity = OSClient(host_url,client_id,username,password)

        def test_list_local_users(self):
          """
          list all the users
          """
          status = self.identity.list_local_users(tenant_id)
          self.identity.resp_logging(200, status)

        def test_create_local_user(self):
          """
          create local user
          """
          data = { "active": "true", "displayName": "test", "userName": "test@hpe.com", "password": "Cloud@123","name": {"familyName":"Jensen","givenName":"Barbara"}}
          status = self.identity.create_local_user(data,tenant_id)
          result = status.json()
          self.identity.resp_logging(201, status)
          assert result['displayName'] == "test"
          assert result['userName'] == "test@hpe.com"

        def test_delete_local_user(self):
          """
          delete user(according to SCIM spec 2.0)
          """
          data = { "active": "true", "displayName": "automation", "userName": "automation@hpe.com", "password": "Cloud@123","name": {"familyName":"delete","givenName":"user"}}
          status = self.identity.create_local_user(data,tenant_id)
          result = status.json()
          print status.status_code
          if status.status_code == 201:
              user_id = result['id']
              deleted_status = self.identity.delete_local_user(tenant_id,user_id)
              self.identity.resp_logging(204, deleted_status)
          else:
             print "User creation failed"

