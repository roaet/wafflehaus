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
from wafflehaus.try_context import context_filter
from tests import test_base


class TestContextClass(object):
    pass


class TestTryContext(test_base.TestBase):
    def setUp(self):
        super(TestTryContext, self).setUp()
        self.app = mock.Mock()
        self.app.return_value = "OK"
        self.start_response = mock.Mock()
        self.test_cls = "tests.test_try_context.TestContextClass"

        self.req = {'REQUEST_METHOD': 'HEAD',
                    'X_USER_ID': '12345', }

        self.local_conf = {"context_class": self.test_cls,
                           "context_key": "context.test", }

        self.strat_neutron = {"context_strategy": "neutron"}
        self.strat_none = {"context_strategy": "none"}
        self.strat_test = {"context_strategy": "test"}

    def test_create_strategy_test(self):
        """This is a test strategy to see if this thing works"""
        result = context_filter.filter_factory(self.strat_test)(self.app)
        self.assertTrue(isinstance(result, context_filter.TestContextFilter))
        self.assertEqual('OK', result(self.req, self.start_response))

    def test_create_strategy_none(self):
        """The none strategy simply is a noop."""
        result = context_filter.filter_factory(self.strat_none)(self.app)
        self.assertIsNotNone(result)
        self.assertTrue(not isinstance(result, context_filter.ContextFilter))
        self.assertEqual('OK', result(self.req, self.start_response))

    def test_create_strategy_neutron(self):
        """Attempt to create the neutron strategy if it is installed. This
        will probably never run inside of tox because test-requirements are
        weird."""
        try:
            from neutron import context
            context
        except ImportError as e:
            self.skipTest("Neutron not installed. " + str(e))
        result = context_filter.filter_factory(self.strat_neutron)(self.app)
        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result,
                                   context_filter.NeutronContextFilter))
        self.assertFalse('neutron.context' in self.req)
        headers = {'Content-Type': 'application/json',
                   'X_USER_ID': 'derp', }
        resp = result.__call__.request('/', method='HEAD', headers=headers)
        self.assertEqual(self.app, resp)
        self.assertFalse('neutron.context' in self.req)

    def test_create_strategy_neutron_no_user(self):
        """Attempt to create the neutron strategy if it is installed. This
        will probably never run inside of tox because test-requirements are
        weird."""
        try:
            from neutron import context
            context
        except ImportError as e:
            self.skipTest("Neutron not installed. " + str(e))
        result = context_filter.filter_factory(self.strat_neutron)(self.app)
        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result,
                                   context_filter.NeutronContextFilter))
        self.assertFalse('neutron.context' in self.req)
        headers = {'Content-Type': 'application/json', }
        resp = result.__call__.request('/', method='HEAD', headers=headers)
        self.assertEqual(401, resp.status_code)
