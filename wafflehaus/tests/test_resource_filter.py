# Copyright 2015 Rackspace Hosting
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
import mock
import webob.exc

from wafflehaus.resource_filter import block_resource
from wafflehaus import tests


class TestResourceFilter(tests.TestCase):
    def setUp(self):
        self.app = mock.Mock()

        self.simple_conf1 = {'resource': 'PoST /widget', 'enabled': 'true'}
        self.simple_conf2 = {'resource': 'PoSt GeT /widget', 'enabled': 'true'}
        self.multi_conf = {'resource': 'post GET /widget, GET posT /derp',
                           'enabled': 'true'}
        self.collapse_conf = {'resource': 'posT /widget, GET /widget',
                              'enabled': 'true'}
        self.complex_conf = {'resource': 'posT /widget/{id}/sub/{sub_id}',
                             'enabled': 'true'}
        self.format_conf1 = {'resource': 'POST /widget{.format:json|xml}',
                             'enabled': 'true'}

    def test_default_instance_create_simple(self):
        result = block_resource.filter_factory(self.simple_conf1)(self.app)
        self.assertIsNotNone(result)
        self.assertTrue(hasattr(result, 'resources'))
        self.assertTrue(isinstance(result.resources, dict))
        self.assertEqual(1, len(result.resources))
        resources = result.resources
        self.assertTrue('/widget' in resources)
        self.assertEqual(1, len(resources['/widget']))

    def test_default_instance_create_simple_multi_method(self):
        result = block_resource.filter_factory(self.simple_conf2)(self.app)
        resources = result.resources
        widget = resources['/widget']
        self.assertEqual(2, len(widget))
        self.assertTrue('POST' in widget)
        self.assertTrue('GET' in widget)

    def test_default_instance_create_multi(self):
        result = block_resource.filter_factory(self.multi_conf)(self.app)
        resources = result.resources
        self.assertEqual(2, len(resources))
        for k, res in resources.iteritems():
            self.assertEqual(2, len(res))
            self.assertTrue('POST' in res)
            self.assertTrue('GET' in res)

    def test_default_instance_collapse(self):
        result = block_resource.filter_factory(self.collapse_conf)(self.app)
        resources = result.resources
        self.assertEqual(1, len(resources))
        widget = resources['/widget']
        self.assertEqual(2, len(widget))
        self.assertTrue('POST' in widget)
        self.assertTrue('GET' in widget)

    def test_match_route(self):
        result = block_resource.filter_factory(self.simple_conf1)(self.app)
        resp = result.__call__.request('/widget', method='POST')
        self.assertTrue(isinstance(resp, webob.exc.HTTPException))

    def test_match_formatted_route1(self):
        result = block_resource.filter_factory(self.format_conf1)(self.app)
        resp = result.__call__.request('/cog', method='POST')
        self.assertEqual(self.app, resp)

        resp = result.__call__.request('/widget', method='POST')
        self.assertTrue(isinstance(resp, webob.exc.HTTPException))
        resp = result.__call__.request('/widget', method='PUT')
        self.assertEqual(self.app, resp)

        resp = result.__call__.request('/widget.json', method='POST')
        self.assertTrue(isinstance(resp, webob.exc.HTTPException))
        resp = result.__call__.request('/widget.json', method='PUT')
        self.assertEqual(self.app, resp)

        resp = result.__call__.request('/widget.xml', method='POST')
        self.assertTrue(isinstance(resp, webob.exc.HTTPException))
        resp = result.__call__.request('/widget.xml', method='PUT')
        self.assertEqual(self.app, resp)

        resp = result.__call__.request('/widget.derp', method='POST')
        self.assertEqual(self.app, resp)
        resp = result.__call__.request('/widget.derp', method='PUT')
        self.assertEqual(self.app, resp)

    def test_match_multi_route(self):
        result = block_resource.filter_factory(self.multi_conf)(self.app)
        resp = result.__call__.request('/widget', method='POST')
        self.assertTrue(isinstance(resp, webob.exc.HTTPException))
        resp = result.__call__.request('/derp', method='POST')
        self.assertTrue(isinstance(resp, webob.exc.HTTPException))
        resp = result.__call__.request('/widget', method='GET')
        self.assertTrue(isinstance(resp, webob.exc.HTTPException))
        resp = result.__call__.request('/derp', method='GET')
        self.assertTrue(isinstance(resp, webob.exc.HTTPException))
        resp = result.__call__.request('/widget', method='PUT')
        self.assertEqual(self.app, resp)
        resp = result.__call__.request('/derp', method='PUT')
        self.assertEqual(self.app, resp)

    def test_match_complex_route(self):
        result = block_resource.filter_factory(self.complex_conf)(self.app)
        resp = result.__call__.request('/widget', method='POST')
        self.assertEqual(self.app, resp)
        resp = result.__call__.request('/widget/1234/sub/1234', method='POST')
        self.assertTrue(isinstance(resp, webob.exc.HTTPException))

    def test_fail_to_match_route(self):
        result = block_resource.filter_factory(self.simple_conf1)(self.app)
        resp = result.__call__.request('/willfail', method='POST')
        self.assertEqual(self.app, resp)

    def test_fail_to_match_method(self):
        result = block_resource.filter_factory(self.simple_conf1)(self.app)
        resp = result.__call__.request('/widget', method='GET')
        self.assertEqual(self.app, resp)

    def test_override_runtime(self):
        self.set_reconfigure()
        result = block_resource.filter_factory(self.simple_conf1)(self.app)
        headers = {'X_WAFFLEHAUS_BLOCKRESOURCE_ENABLED': False}
        resp = result.__call__.request('/widget', method='POST',
                                       headers=headers)
        self.assertEqual(self.app, resp)
        headers = {'X_WAFFLEHAUS_BLOCKRESOURCE_ENABLED': True}
        resp = result.__call__.request('/widget', method='POST',
                                       headers=headers)
        self.assertTrue(isinstance(resp, webob.exc.HTTPException))
        headers = {'X_WAFFLEHAUS_BLOCKRESOURCE_RESOURCE': 'GET /derp'}
        resp = result.__call__.request('/widget', method='POST',
                                       headers=headers)
        self.assertEqual(self.app, resp)
        resp = result.__call__.request('/derp', method='GET',
                                       headers=headers)
        self.assertTrue(isinstance(resp, webob.exc.HTTPException))
