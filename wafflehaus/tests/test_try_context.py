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
import mock
import webob.exc

from wafflehaus import tests
from wafflehaus.try_context import context_filter


class TestContextClass(context_filter.BaseContextStrategy):
    def __init__(self, key, req_auth=False):
        super(TestContextClass, self).__init__(key, req_auth)
        self._mockme()
        if req_auth:
            self._auth_required()

    def _mockme(self):
        """Exists because one can't mock __init__."""
        pass

    def _auth_required(self):
        """Exists because one can't mock __init__."""
        pass


class TestTryContext(tests.TestCase):

    def setUp(self):
        super(TestTryContext, self).setUp()
        self.app = mock.Mock()
        self.app.return_value = "OK"
        self.start_response = mock.Mock()
        self.test_cls = "wafflehaus.tests.test_try_context.TestContextClass"
        self.context_init = self.create_patch(self.test_cls + '._mockme')
        self.auth_check = self.create_patch(self.test_cls + '._auth_required')

        self.strat_test_auth = {"context_strategy": self.test_cls,
                                'enabled': 'true',
                                'require_auth_info': True,
                                "context_key": "context.test", }

        self.strat_test = {"context_strategy": self.test_cls,
                           'enabled': 'true',
                           "context_key": "context.test", }

        self.strat_testing = {"context_strategy": self.test_cls,
                              "context_key": "context.test",
                              'enabled': 'true',
                              "testing": "true"}

        self.unknown = {"context_strategy": "unknown.class",
                        'enabled': 'true',
                        "context_key": "context.test", }

        self.unknown_testing = {"context_strategy": "unknown.class",
                                "context_key": "context.test",
                                'enabled': 'true',
                                "testing": "true"}
        self.get_admin_mock = mock.Mock()
        self.get_admin_mock.return_value = ['admin']

    def test_create_strategy_test(self):
        """This is a test strategy to see if this thing works."""
        result = context_filter.filter_factory(self.strat_test)(self.app)
        self.assertTrue(isinstance(result, context_filter.ContextFilter))
        resp = result.__call__.request('/something', method='HEAD')
        self.assertEqual(self.app, resp)
        self.assertEqual(1, self.context_init.call_count)
        self.assertEqual(0, self.auth_check.call_count)
        self.assertTrue(isinstance(result, context_filter.ContextFilter))
        """Should be 1 because of a new instance."""
        self.assertEqual(1, self.context_init.call_count)

    def test_create_strategy_test_required_auth(self):
        """This is a test strategy to see if this thing works."""
        result = context_filter.filter_factory(self.strat_test_auth)(self.app)
        self.assertTrue(isinstance(result, context_filter.ContextFilter))
        resp = result.__call__.request('/something', method='HEAD')
        self.assertEqual(self.app, resp)
        self.assertEqual(1, self.context_init.call_count)
        self.assertEqual(1, self.auth_check.call_count)
        self.assertTrue(isinstance(result, context_filter.ContextFilter))
        """Should be 1 because of a new instance."""
        self.assertEqual(1, self.context_init.call_count)

    def test_create_strategy_test_noop_testing(self):
        """This is a test strategy to see if this thing works."""
        result = context_filter.filter_factory(self.strat_test)(self.app)
        self.assertTrue(isinstance(result, context_filter.ContextFilter))
        resp = result.__call__.request('/something', method='HEAD')
        self.assertEqual(self.app, resp)
        self.assertEqual(1, self.context_init.call_count)
        self.assertTrue(isinstance(result, context_filter.ContextFilter))
        """Should be 1 because of a new instance."""
        self.assertEqual(1, self.context_init.call_count)

    def test_create_strategy_none(self):
        """The none strategy simply is a noop."""
        result = context_filter.filter_factory({})(self.app)
        self.assertIsNotNone(result)
        resp = result.__call__.request('/something', method='HEAD')
        self.assertTrue(isinstance(result, context_filter.ContextFilter))
        self.assertEqual(self.app, resp)

    def test_create_strategy_unknown_should_500(self):
        """The none strategy simply is a noop."""
        result = context_filter.filter_factory(self.unknown)(self.app)
        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, context_filter.ContextFilter))
        resp = result.__call__.request('/something', method='HEAD')
        self.assertNotEqual(self.app, resp)
        self.assertTrue(isinstance(resp, webob.exc.HTTPInternalServerError))

    def test_create_strategy_unknown_should_500_noop_testing(self):
        """The none strategy simply is a noop."""
        result = context_filter.filter_factory(self.unknown_testing)(self.app)
        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, context_filter.ContextFilter))
        resp = result.__call__.request('/something', method='HEAD')
        self.assertEqual(self.app, resp)

    def test_override_runtime_enabled(self):
        """The none strategy simply is a noop."""
        self.set_reconfigure()
        headers = {'X_WAFFLEHAUS_CONTEXTFILTER_ENABLED': False}
        result = context_filter.filter_factory(self.strat_test)(self.app)
        self.assertTrue(isinstance(result, context_filter.ContextFilter))
        resp = result.__call__.request('/something', method='HEAD',
                                       headers=headers)
        self.assertEqual(self.app, resp)
        self.assertEqual(0, self.context_init.call_count)
        self.assertTrue(isinstance(result, context_filter.ContextFilter))
        """Should be 1 because of a new instance."""
        self.assertEqual(0, self.context_init.call_count)
