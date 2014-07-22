# Copyright 2013 Openstack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import json

import mock
import webob

from wafflehaus import edit_response
from wafflehaus import tests

class TestEditResponse(tests.TestCase):
    def setUp(self):
        super(TestEditResponse, self).setUp()
        self.app = self._fake_app
        self.body = {"result":
                        {"passcode": "123password",
                         "combination": "1,2,3,4",
                         "secret": "no pants",
                         "recipe": "raw chicken, razzle dazzle"}}
        self.conf = {"enabled": "true",
                     "filters": "safe, secret",
                     "safe_resource": "POST /data",
                     "safe_key": "combination",
                     "safe_value": "REDACTED",
                     "secret_resource": "GET /data",
                     "secret_key": "secret"}
        self.delete_conf = {"enabled": "true",
                            "filters": "super_secret",
                            "super_secret_resource": "PUT /secrets",
                            "super_secret_key": "passcode"}
        self.redact_conf = {"enabled": "true",
                            "filters": "secret",
                            "secret_resource": "GET /sauce",
                            "secret_key": "recipe",
                            "secret_value": "REDACTED"}

                     

    @webob.dec.wsgify
    def _fake_app(self, req):
        return webob.Response(body=json.dumps(self.body), status=200)

    def test_filter_creation(self):
        test_filter = edit_response.filter_factory(self.conf)(self.app)

        self.assertIsNotNone(test_filter)
        self.assertIsInstance(test_filter, edit_response.EditResponse)
        self.assertTrue(callable(test_filter))

    def test_disabled_filter(self):
        conf = {"enabled":"false"}
        test_filter = edit_response.filter_factory(conf)(self.app)
        resp = test_filter(webob.Request.blank("/cheeseburger", method="GET"))

        self.assertEqual(resp, self.app)

    def test_attrib_rename(self):
        test_filter = edit_response.filter_factory(self.redact_conf)(self.app)
        resp = test_filter(webob.Request.blank("/sauce", method="GET"))
        new_body = self.body
        new_body["result"]["recipe"] = "REDACTED"

        self.assertEqual(resp.body, json.dumps(new_body))

    def test_attrib_deletion(self):
        pass

    def test_attrib_combo(self):
        pass

    def test_resource_with_alternate_methods(self):
        pass

    def test_garbage(self):
        pass

    def test_case_sensitivity(self):
        pass
