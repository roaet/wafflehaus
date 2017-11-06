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

from wafflehaus.payload_filter import unset_key
from wafflehaus import tests

"""The request gets modified with the self.conf values,these values gets
attached to the request"""


class TestPayloadFilter(tests.TestCase):
    def setUp(self):
        self.app = mock.Mock()
        simple_widget = 'widget:thing=thingie'
        complex_widget = 'widget:sub:thing=thingie'
        multi_widget = 'widgets:thing=thingie'
        multi_subwidget = 'widgets:sub:thing=thingie'
        self.simple_conf1 = {'resource': 'POST /widget', 'enabled': 'true',
                             'defaults': simple_widget}
        self.simple_conf2 = {'resource': 'POST /widget', 'enabled': 'true',
                             'defaults': complex_widget}
        self.multi_conf = {'resource': 'POST /widget', 'enabled': 'true',
                           'defaults': '%s,%s' % (simple_widget,
                                                  complex_widget)}
        self.multi_confr = {'resource': 'POST /widget', 'enabled': 'true',
                            'defaults': '%s,%s' % (complex_widget,
                                                   simple_widget)}
        self.plural_conf = {'resource': 'POST /widget', 'enabled': 'true',
                            'defaults': multi_widget}
        self.plural_conf2 = {'resource': 'POST /widget', 'enabled': 'true',
                             'defaults': multi_subwidget}

        self.body1 = '{"widget": { "name": "foo"}}'
        self.body2 = '{"widget": { "name": "foo", "thing": "derp"}}'
        self.body3 = '{"widget": { "name": "foo", "sub": { "name": "bar"}}}'
        self.body4 = '{"widgets": [{"name": "1"},{"name": "2"}]}'
        self.body5 = '{"widgets": [{"sub":{"name": "1"}}]}'

    def test_default_instance_create_simple(self):
        result = unset_key.filter_factory(self.simple_conf1)(self.app)
        self.assertIsNotNone(result)
        self.assertTrue(hasattr(result, 'resources'))
        self.assertTrue(isinstance(result.resources, dict))
        self.assertEqual(1, len(result.resources))
        resources = result.resources
        self.assertTrue('/widget' in resources)
        self.assertEqual(1, len(resources['/widget']))

    def test_request_body_overridden(self):
        """Payload filter will set values for keys that do not exist, should not

        modify the existing keys
        """

        result = unset_key.filter_factory(self.simple_conf1)(self.app)
        # using the webob for creating request objiect
        req = webob.Request.blank('/widget', method='POST', body=self.body1)
        # Before call the keys are not present in the request
        self.assertTrue('thing' not in req.body)
        # calling the api , by making the actual request
        resp = result.__call__(req)
        # assert if the response is not null
        self.assertEqual(self.app, resp)
        # result is the request after the keys are set , unset key is misnomer
        body = req.body
        self.assertEqual(result.body, req.body)
        self.assertIsNotNone(body)
        json_body = json.loads(body)
        # request body will be having  by the config passed
        self.assertTrue('widget' in json_body)
        # thing , thingie would be added to the request inside widget
        self.assertTrue('thing' not in json_body)
        widget = json_body['widget']
        self.assertTrue('name' in widget)
        self.assertEqual('foo', widget['name'])
        # assert that thing is present in the widget
        self.assertTrue('thing' in widget)
        self.assertEqual('thingie', widget['thing'])

    def test_request_body_not_overridden(self):
        """Payload filter will not change values that are set."""
        # already existing keys should not be reset
        result = unset_key.filter_factory(self.simple_conf1)(self.app)
        # request object
        req = webob.Request.blank('/widget', method='POST', body=self.body2)
        request_json = json.loads(req.body)
        self.assertEqual('derp', request_json['widget']['thing'])
        # api call with the request
        resp = result.__call__(req)
        self.assertEqual(self.app, resp)
        body = req.body
        self.assertEqual(req.body, result.body)
        self.assertIsNotNone(body)
        json_body = json.loads(body)
        self.assertTrue('widget' in json_body)
        self.assertTrue('thing' not in json_body)
        widget = json_body['widget']
        self.assertTrue('name' in widget)
        self.assertEqual('foo', widget['name'])
        self.assertTrue('thing' in widget)
        self.assertEqual('derp', widget['thing'])

    def test_request_complex_path(self):
        """Complex path e.g. widget:sub:thing=thinge"""
        # thing:thinge should be added to the json widget['sub']

        result = unset_key.filter_factory(self.simple_conf2)(self.app)
        req = webob.Request.blank('/widget', method='POST', body=self.body3)
        request_json = json.loads(req.body)
        self.assertTrue('thing' not in request_json['widget']['sub'])
        resp = result.__call__(req)
        self.assertEqual(self.app, resp)
        body = req.body
        self.assertEqual(req.body, result.body)
        self.assertIsNotNone(body)
        json_body = json.loads(body)
        self.assertTrue('widget' in json_body)
        self.assertTrue('thing' not in json_body)
        widget = json_body['widget']
        self.assertTrue('thing' not in widget)
        self.assertTrue('name' in widget)
        self.assertEqual('foo', widget['name'])
        self.assertTrue('sub' in widget)
        sub = widget['sub']
        self.assertEqual('thingie', sub['thing'])
        # assert that existing key value is not modified for complex path
        self.assertEqual('bar', sub['name'])

    def test_request_multi_path(self):
        """Multipath includes two paths together , simple and complex and

        should be added to the payload accordingly
        """
        result = unset_key.filter_factory(self.multi_conf)(self.app)
        req = webob.Request.blank('/widget', method='POST', body=self.body3)
        request_json = json.loads(req.body)
        self.assertTrue('thing' not in request_json['widget'])
        self.assertTrue('sub' not in request_json['widget']['sub'])
        resp = result.__call__(req)
        self.assertEqual(self.app, resp)
        body = req.body
        self.assertEqual(req.body, result.body)
        self.assertIsNotNone(body)
        json_body = json.loads(body)
        self.assertTrue('widget' in json_body)
        widget = json_body['widget']
        # existing keys should not be modified
        self.assertTrue('name' in widget)
        self.assertEqual('foo', widget['name'])
        # simple conf params are added to the request payload
        self.assertTrue('thing' in widget)
        self.assertEqual('thingie', widget['thing'])
        # complex conf params are added to the request payload
        self.assertTrue('sub' in widget)
        sub = widget['sub']
        self.assertEqual('thingie', sub['thing'])

    def test_request_multi_path_with_part_missing(self):
        """Body has 'sub' keyword missing """
        result = unset_key.filter_factory(self.multi_conf)(self.app)
        req = webob.Request.blank('/widget', method='POST', body=self.body1)
        self.assertTrue('thing' not in req.body)
        self.assertTrue('sub' not in req.body)
        resp = result.__call__(req)
        self.assertEqual(self.app, resp)
        body = req.body
        self.assertEqual(req.body, result.body)
        self.assertIsNotNone(body)
        json_body = json.loads(body)
        self.assertTrue('widget' in json_body)
        widget = json_body['widget']
        self.assertTrue('name' in widget)
        self.assertEqual('foo', widget['name'])
        self.assertTrue('thing' in widget)
        self.assertEqual('thingie', widget['thing'])
        # since the key is not there its path to the sub:thing is missing
        self.assertFalse('sub' in widget)

    def test_request_multi_path_with_part_missing_reversed(self):
        """Simple_widget, complex_widget in reverse order."""
        result = unset_key.filter_factory(self.multi_confr)(self.app)
        req = webob.Request.blank('/widget', method='POST', body=self.body1)
        self.assertTrue('thing' not in req.body)
        self.assertTrue('sub' not in req.body)
        resp = result.__call__(req)
        self.assertEqual(self.app, resp)
        body = req.body
        self.assertEqual(req.body, result.body)
        self.assertIsNotNone(body)
        json_body = json.loads(body)
        self.assertTrue('widget' in json_body)
        widget = json_body['widget']
        self.assertTrue('name' in widget)
        self.assertEqual('foo', widget['name'])
        self.assertTrue('thing' in widget)
        self.assertEqual('thingie', widget['thing'])
        # since the key is not there its path to the sub:thing is missing
        self.assertFalse('sub' in widget)

    def test_request_plural_request(self):
        """widgets value as list of json,rather than a single json."""
        result = unset_key.filter_factory(self.plural_conf)(self.app)
        req = webob.Request.blank('/widget', method='POST', body=self.body4)
        self.assertTrue('thing' not in req.body)
        resp = result.__call__(req)
        self.assertEqual(self.app, resp)
        body = req.body
        self.assertEqual(req.body, result.body)
        self.assertIsNotNone(body)
        json_body = json.loads(body)
        self.assertTrue('widgets' in json_body)
        self.assertTrue('thing' not in json_body)
        widgets = json_body['widgets']
        # In this case the key and value (eg:thing and thinge) gets attached
        # to each json
        for widget in widgets:
            self.assertTrue('name' in widget)
            self.assertTrue('thing' in widget)
            self.assertEqual('thingie', widget['thing'])

    def test_request_plural_sub_request(self):
        """Plural subrequest."""
        result = unset_key.filter_factory(self.plural_conf2)(self.app)
        req = webob.Request.blank('/widget', method='POST', body=self.body5)
        self.assertTrue('thing' not in req.body)
        resp = result.__call__(req)
        self.assertEqual(self.app, resp)
        body = req.body
        self.assertEqual(req.body, result.body)
        self.assertIsNotNone(body)
        json_body = json.loads(body)
        self.assertTrue('widgets' in json_body)
        self.assertTrue('thing' not in json_body)
        widgets = json_body['widgets']
        for widget in widgets:
            self.assertTrue('thing' not in widget)
            self.assertTrue('sub' in widget)
            sub = widget['sub']
            self.assertTrue('name' in sub)
            self.assertTrue('thing' in sub)
            self.assertEqual('thingie', sub['thing'])

    def test_override_runtime(self):
        """Modify the request headers, request before and after

        X_WAFFLEHAUS_DEFAULTPAYLOAD_ENABLED set as false and true.
        """

        self.set_reconfigure()
        result = unset_key.filter_factory(self.plural_conf2)(self.app)
        headers = {'X_WAFFLEHAUS_DEFAULTPAYLOAD_ENABLED': False}
        req = webob.Request.blank('/widget', method='POST', body=self.body5,
                                  headers=headers)
        resp = result.__call__(req)
        self.assertEqual(self.app, resp)
        self.assertFalse(hasattr(result, 'body'))
        headers = {'X_WAFFLEHAUS_DEFAULTPAYLOAD_ENABLED': True}
        req = webob.Request.blank('/widget', method='POST', body=self.body5,
                                  headers=headers)
        resp = result.__call__(req)
        self.assertEqual(self.app, resp)
        self.assertTrue(hasattr(result, 'body'))
