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

        def test_list_available_idps(self):
          """
          list all the available idps for the given token.
          """
          status = self.identity.list_idps(tenant_id)
          self.identity.resp_logging(200, status)

        def test_list_idpusers(self):
          """
          list all the users for the given token.
          """
          status = self.identity.list_users(tenant_id)
          self.identity.resp_logging(200, status)

        def test_list_idpuser_byid(self):
          """
          list user by id.
          """
          status = self.identity.list_users(tenant_id)
          result = status.json()
          user_id = result['resources'][0]['id']
          user_status = self.identity.list_users(user_id) 
          self.identity.resp_logging(200, user_status)

        def test_list_idpgroups(self):
          """
          list all the groups for the given token.
          """
          status = self.identity.list_groups(tenant_id)
          self.identity.resp_logging(200, status)

        def test_list_idpgroup_byid(self):
          """
          list group by id.
          """
          status = self.identity.list_groups(tenant_id)
          result = status.json()
          group_id = result['resources'][0]['id']
          group_status = self.identity.list_groups(group_id)
          self.identity.resp_logging(200, group_status)

