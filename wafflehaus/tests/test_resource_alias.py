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

from wafflehaus.resource_filter import alias
from wafflehaus import tests


class TestResourceFilter(tests.TestCase):
    def setUp(self):
        self.app = mock.Mock()
        self.conf1 = {'resource': '/widget', 'enabled': 'true',
                      'action': ''}
        self.conf2 = {'resource': '/widget', 'enabled': 'true',
                      'action': '301:/cog'}
        self.conf3 = {'resource': '/widget', 'enabled': 'true',
                      'action': 'addslash'}
        self.conf4 = {'resource': '/widget', 'enabled': 'true',
                      'action': 'subrequest:/cog'}

    def test_default_instance_create_simple(self):
        result = alias.filter_factory(self.conf1)(self.app)
        self.assertIsNotNone(result)
        self.assertTrue(hasattr(result, 'resources'))
        self.assertTrue(isinstance(result.resources, dict))
        self.assertEqual(1, len(result.resources))
        resources = result.resources
        self.assertTrue('/widget' in resources)
        widget = resources['/widget']
        self.assertTrue('POST' in widget)
        self.assertTrue('GET' in widget)
        self.assertTrue('PUT' in widget)
        self.assertTrue('DELETE' in widget)
        self.assertTrue('HEAD' in widget)
        self.assertTrue('OPTION' in widget)

    def test_400_on_resource(self):
        result = alias.filter_factory(self.conf1)(self.app)
        resp = result.__call__.request('/widget', method='POST')
        self.assertTrue(isinstance(resp, webob.exc.HTTPBadRequest))
        resp = result.__call__.request('/widget', method='GET')
        self.assertTrue(isinstance(resp, webob.exc.HTTPBadRequest))
        resp = result.__call__.request('/widget', method='PUT')
        self.assertTrue(isinstance(resp, webob.exc.HTTPBadRequest))
        resp = result.__call__.request('/widget', method='DELETE')
        self.assertTrue(isinstance(resp, webob.exc.HTTPBadRequest))
        resp = result.__call__.request('/widget', method='HEAD')
        self.assertTrue(isinstance(resp, webob.exc.HTTPBadRequest))
        resp = result.__call__.request('/widget', method='OPTION')
        self.assertTrue(isinstance(resp, webob.exc.HTTPBadRequest))

        resp = result.__call__.request('/widgets', method='POST')
        self.assertEqual(self.app, resp)
        resp = result.__call__.request('/widgets', method='GET')
        self.assertEqual(self.app, resp)
        resp = result.__call__.request('/widgets', method='PUT')
        self.assertEqual(self.app, resp)
        resp = result.__call__.request('/widgets', method='DELETE')
        self.assertEqual(self.app, resp)
        resp = result.__call__.request('/widgets', method='HEAD')
        self.assertEqual(self.app, resp)
        resp = result.__call__.request('/widgets', method='OPTION')
        self.assertEqual(self.app, resp)

    def test_301_on_resource(self):
        result = alias.filter_factory(self.conf2)(self.app)
        resp = result.__call__.request('/widget', method='POST')
        self.assertTrue(isinstance(resp, webob.exc.HTTPMovedPermanently))
        resp = result.__call__.request('/widget', method='GET')
        self.assertTrue(isinstance(resp, webob.exc.HTTPMovedPermanently))
        resp = result.__call__.request('/widget', method='PUT')
        self.assertTrue(isinstance(resp, webob.exc.HTTPMovedPermanently))
        resp = result.__call__.request('/widget', method='DELETE')
        self.assertTrue(isinstance(resp, webob.exc.HTTPMovedPermanently))
        resp = result.__call__.request('/widget', method='HEAD')
        self.assertTrue(isinstance(resp, webob.exc.HTTPMovedPermanently))
        resp = result.__call__.request('/widget', method='OPTION')
        self.assertTrue(isinstance(resp, webob.exc.HTTPMovedPermanently))

        resp = result.__call__.request('/widgets', method='POST')
        self.assertEqual(self.app, resp)
        resp = result.__call__.request('/widgets', method='GET')
        self.assertEqual(self.app, resp)
        resp = result.__call__.request('/widgets', method='PUT')
        self.assertEqual(self.app, resp)
        resp = result.__call__.request('/widgets', method='DELETE')
        self.assertEqual(self.app, resp)
        resp = result.__call__.request('/widgets', method='HEAD')
        self.assertEqual(self.app, resp)
        resp = result.__call__.request('/widgets', method='OPTION')
        self.assertEqual(self.app, resp)

    def test_add_slash_on_resource(self):
        result = alias.filter_factory(self.conf3)(self.app)
        resp = result.__call__.request('/widget', method='POST')
        self.assertTrue(isinstance(resp, webob.exc.HTTPMovedPermanently))
        resp = result.__call__.request('/widget', method='GET')
        self.assertTrue(isinstance(resp, webob.exc.HTTPMovedPermanently))
        resp = result.__call__.request('/widget', method='PUT')
        self.assertTrue(isinstance(resp, webob.exc.HTTPMovedPermanently))
        resp = result.__call__.request('/widget', method='DELETE')
        self.assertTrue(isinstance(resp, webob.exc.HTTPMovedPermanently))
        resp = result.__call__.request('/widget', method='HEAD')
        self.assertTrue(isinstance(resp, webob.exc.HTTPMovedPermanently))
        resp = result.__call__.request('/widget', method='OPTION')
        self.assertTrue(isinstance(resp, webob.exc.HTTPMovedPermanently))

        resp = result.__call__.request('/widgets', method='POST')
        self.assertEqual(self.app, resp)
        resp = result.__call__.request('/widgets', method='GET')
        self.assertEqual(self.app, resp)
        resp = result.__call__.request('/widgets', method='PUT')
        self.assertEqual(self.app, resp)
        resp = result.__call__.request('/widgets', method='DELETE')
        self.assertEqual(self.app, resp)
        resp = result.__call__.request('/widgets', method='HEAD')
        self.assertEqual(self.app, resp)
        resp = result.__call__.request('/widgets', method='OPTION')
        self.assertEqual(self.app, resp)
