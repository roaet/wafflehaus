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
        self.body = {"OK": "I'm a lumberjack"}
        self.conf = {"enabled": "true",
                     "filters": "secret, super_secret",
                     "secret_resource": "GET /sauce",
                     "secret_key": "recipe",
                     "secret_value": "REDACTED",
                     "super_secret_resource": "GET /sauce",
                     "super_secret_key": "passcode"}
                     

    @webob.dec.wsgify
    def _fake_app(self, req):
        return webob.Response(body=json.dumps(self.body), status=200)

    def test_filter_creation(self):
        test_filter = edit_response.filter_factory(self.conf)(self.app)

        self.assertIsNotNone(test_filter)
        self.assertIsInstance(test_filter, edit_response.EditResponse)
        self.assertTrue(callable(test_filter))
