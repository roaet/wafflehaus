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
        self.combo_conf = {"enabled": "true",
                           "filters": "safe secret",
                           "safe_resource": "POST /data",
                           "safe_key": "combination",
                           "safe_value": "REDACTED",
                           "secret_resource": "POST /data",
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
        self.make_empty = {"enabled": "true",
                           "filters": "result",
                           "result_resource": "GET /sauce",
                           "result_key": "result",
                           "result_value": "[]"}
        self.make_null = {"enabled": "true",
                          "filters": "result",
                          "result_resource": "GET /sauce",
                          "result_key": "result",
                          "result_value": "NULL"}
        self.keep_if = {"enabled": "true",
                        "filters": "result",
                        "result_resource": "GET /sauce",
                        "result_key": "results",
                        "result_value": "foreach:keep_if:some=here"}
        self.drop_if = {"enabled": "true",
                        "filters": "result",
                        "result_resource": "GET /sauce",
                        "result_key": "results",
                        "result_value": "foreach:drop_if:some=here"}
        self.test_none = {"enabled": "true",
                          "filters": "result",
                          "result_resource": "GET /sauce/{id}",
                          "result_key": "result",
                          "result_value": "NULL"}

    @webob.dec.wsgify
    def _fake_app(self, req, body=None):
        if body is None:
            body = self.body
        return webob.Response(body=json.dumps(body), status=200)

    def test_filter_creation(self):
        test_filter = edit_response.filter_factory(self.combo_conf)(self.app)

        self.assertIsNotNone(test_filter)
        self.assertIsInstance(test_filter, edit_response.EditResponse)
        self.assertTrue(callable(test_filter))

    def test_keep_if(self):
        app_body = {"results":
                    [{"some": "here"}, {"some": "there"}, {"derp": "derp"}]}
        processed_body = {"results":
                          [{"some": "there"}, {"derp": "derp"}]}

        @webob.dec.wsgify
        def app(req):
            return webob.Response(body=json.dumps(app_body), status=200)
        test_filter = edit_response.filter_factory(self.drop_if)(app)
        resp = test_filter(webob.Request.blank("/sauce", method="GET"))

        self.assertEqual(resp.json, processed_body)

    def test_drop_if(self):
        app_body = {"results":
                    [{"some": "here"}, {"some": "there"}, {"derp": "derp"}]}
        processed_body = {"results": [{"some": "here"}]}

        @webob.dec.wsgify
        def app(req):
            return webob.Response(body=json.dumps(app_body), status=200)
        test_filter = edit_response.filter_factory(self.keep_if)(app)
        resp = test_filter(webob.Request.blank("/sauce", method="GET"))

        self.assertEqual(resp.json, processed_body)

    def test_disabled_filter(self):
        conf = {"enabled": "false"}
        test_filter = edit_response.filter_factory(conf)(self.app)
        resp = test_filter(webob.Request.blank("/cheeseburger", method="GET"))

        self.assertEqual(resp, self.app)

    def test_attrib_rename(self):
        test_filter = edit_response.filter_factory(self.redact_conf)(self.app)
        resp = test_filter(webob.Request.blank("/sauce", method="GET"))
        new_body = self.body
        new_body["result"]["recipe"] = "REDACTED"

        self.assertEqual(resp.json, new_body)
        self.assertEqual(resp.status_code, 200)

    def test_attrib_deletion(self):
        test_filter = edit_response.filter_factory(self.delete_conf)(self.app)
        resp = test_filter(webob.Request.blank("/secrets", method="PUT"))
        new_body = self.body
        del(new_body['result']['passcode'])

        self.assertEqual(resp.json, new_body)
        self.assertEqual(resp.status_code, 200)

    def test_make_empty(self):
        test_filter = edit_response.filter_factory(self.make_empty)(self.app)
        resp = test_filter(webob.Request.blank("/sauce", method="GET"))
        new_body = json.dumps(dict(result=[]))
        resp_json = json.dumps(json.loads(resp.body))

        self.assertEqual(resp_json, new_body)
        self.assertEqual(resp.status_code, 200)

    def test_make_null(self):
        test_filter = edit_response.filter_factory(self.make_null)(self.app)
        resp = test_filter(webob.Request.blank("/sauce", method="GET"))
        new_body = json.dumps(dict(result=None))
        resp_json = json.dumps(json.loads(resp.body))

        self.assertEqual(resp_json, new_body)
        self.assertEqual(resp.status_code, 200)

    def test_attrib_combo(self):
        test_filter = edit_response.filter_factory(self.combo_conf)(self.app)
        resp = test_filter(webob.Request.blank("/data", method="POST"))
        new_body = self.body
        new_body['result']['combination'] = 'REDACTED'
        del(new_body['result']['secret'])

        self.assertEqual(resp.json, new_body)
        self.assertEqual(resp.status_code, 200)

    def test_resource_with_alternate_methods(self):
        test_filter = edit_response.filter_factory(self.combo_conf)(self.app)
        put_resp = test_filter(webob.Request.blank("/data", method="PUT"))
        get_resp = test_filter(webob.Request.blank("/data", method="GET"))
        head_resp = test_filter(webob.Request.blank("/data", method="HEAD"))

        self.assertEqual(put_resp, self.app)
        self.assertEqual(get_resp, self.app)
        self.assertEqual(head_resp, self.app)

    def test_url_garbage(self):
        test_filter = edit_response.filter_factory(self.combo_conf)(self.app)
        resp1 = test_filter(webob.Request.blank("/gibberish/data",
                                                method="POST"))
        resp2 = test_filter(webob.Request.blank("/hacks?stuff=/data",
                                                method="POST"))
        resp3 = test_filter(webob.Request.blank("/stuffanddata",
                                                method="POST"))

        self.assertEqual(resp1, self.app)
        self.assertEqual(resp2, self.app)
        self.assertEqual(resp3, self.app)

    def test_attrib_case_sensitivity(self):
        app_body = {"results":
                    {"Combination": "DONT LOOK",
                     "SECRET": "<encrypted text>"}}

        @webob.dec.wsgify
        def app(req):
            return webob.Response(body=json.dumps(app_body), status=200)

        test_filter = edit_response.filter_factory(self.combo_conf)(app)
        resp = test_filter(webob.Request.blank("/data", method="POST"))

        self.assertEqual(resp.json, app_body)

    def test_nested_lists_and_dicts(self):
        app_body = {"results":
                    [{"some": "here"},
                     {"some": "there"},
                     ["random_string",
                      {"secret": "MY SECRETS",
                       "nested":
                       {"combination": "1,2,3,4"}}]]}
        processed_body = {"results":
                          [{"some": "here"},
                           {"some": "there"},
                           ["random_string",
                            {"nested":
                             {"combination": "REDACTED"}}]]}

        @webob.dec.wsgify
        def app(req):
            return webob.Response(body=json.dumps(app_body), status=200)

        test_filter = edit_response.filter_factory(self.combo_conf)(app)
        resp = test_filter(webob.Request.blank("/data", method="POST"))

        self.assertEqual(resp.json, processed_body)

    def test_none_request(self):
        app_body = "garbage"

        @webob.dec.wsgify
        def app(req):
            return webob.Response(body=app_body, status=200)
        test_filter = edit_response.filter_factory(self.test_none)(app)
        resp = test_filter(webob.Request.blank("/sauce/None", method="GET"))

        self.assertEqual(resp.body, app_body)

    def test_http_status_replace_get(self):
        app_body = {"garbage": {"garbage": "here"}}

        test_status = {"enabled": "true",
                       "filters": "httpget",
                       "httpget_resource": "GET /sauce",
                       "httpget_key": "http_status_code",
                       "httpget_value": "replace_if:200:201"}

        @webob.dec.wsgify
        def app(req):
            return webob.Response(body=json.dumps(app_body), status=200)
        test_filter = edit_response.filter_factory(test_status)(app)

        resp = test_filter(webob.Request.blank("/sauce", method="GET"))
        self.assertEqual(resp.status_code, 201, resp)

    def test_http_status_replace_post(self):
        app_body = {"garbage": {"garbage": "here"}}

        test_status = {"enabled": "true",
                       "filters": "httppost",
                       "httppost_resource": "POST /sauce",
                       "httppost_key": "http_status_code",
                       "httppost_value": "replace_if:200:201"}

        @webob.dec.wsgify
        def app(req):
            return webob.Response(body=json.dumps(app_body), status=200)
        test_filter = edit_response.filter_factory(test_status)(app)

        resp = test_filter(webob.Request.blank("/sauce", method="POST"))
        self.assertEqual(resp.status_code, 201, resp)

    def test_http_status_replace_put(self):
        app_body = {"garbage": {"garbage": "here"}}

        test_status = {"enabled": "true",
                       "filters": "httpput",
                       "httpput_resource": "PUT /sauce/{id}",
                       "httpput_key": "http_status_code",
                       "httpput_value": "replace_if:200:201"}

        @webob.dec.wsgify
        def app(req):
            return webob.Response(body=json.dumps(app_body), status=200)
        test_filter = edit_response.filter_factory(test_status)(app)

        resp = test_filter(webob.Request.blank("/sauce/id", method="PUT"))
        self.assertEqual(resp.status_code, 201, resp)

    def test_http_status_replace_delete(self):
        app_body = {"garbage": {"garbage": "here"}}

        test_status = {"enabled": "true",
                       "filters": "httpdelete",
                       "httpdelete_resource": "DELETE /sauce/{id}",
                       "httpdelete_key": "http_status_code",
                       "httpdelete_value": "replace_if:200:201"}

        @webob.dec.wsgify
        def app(req):
            return webob.Response(body=json.dumps(app_body), status=200)
        test_filter = edit_response.filter_factory(test_status)(app)

        resp = test_filter(webob.Request.blank("/sauce/id", method="DELETE"))
        self.assertEqual(resp.status_code, 201, resp)
