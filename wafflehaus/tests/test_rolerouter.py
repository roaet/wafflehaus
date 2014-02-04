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
from wafflehaus import rolerouter
from wafflehaus.tests import test_base


class TestRoleRouter(test_base.TestBase):
    def setUp(self):
        super(TestRoleRouter, self).setUp()
        self.local_conf = {"routes": "cat dog",
                           "roles_cat": "domestic outdoor",
                           "roles_dog": "mutt",
                           "route_cat": "cat_filter cat_app",
                           "route_dog": "dog_filter dog_app",
                           "route_default": "appx"}

        def named_mock(name):
            x = mock.Mock()
            x.name = name
            x.return_value = name
            return x

        self.loader = mock.Mock()
        self.loader.get_filter = named_mock
        self.loader.get_app = named_mock

        self.global_conf = {}

    def test_get_default_instance(self):
        result = rolerouter.RoleRouter.factory(self.loader, self.global_conf,
                                               **self.local_conf)
        self.assertTrue(isinstance(result, rolerouter.RoleRouter))
        self.assertEqual(len(result.routes), 3)
        self.assertTrue(all(k in result.routes.keys()
                            for k in ["default", "cat", "dog"]))
        self.assertEqual(len(result.roles), 3)
        self.assertTrue(all(k in result.roles.keys()
                            for k in ["domestic", "outdoor", "mutt"]))

    def test_call_to_domestic_role(self):
        context = mock.Mock()
        context.roles = ["domestic"]

        req = mock.Mock()
        req.environ = {"nova.context": context}

        rr = rolerouter.RoleRouter.factory(self.loader, self.global_conf,
                                           **self.local_conf)
        result = rr(req)
        self.assertEqual(result, "cat_filter")

    def test_call_to_outdoor_role(self):
        context = mock.Mock()
        context.roles = ["outdoor"]

        req = mock.Mock()
        req.environ = {"nova.context": context}

        rr = rolerouter.RoleRouter.factory(self.loader, self.global_conf,
                                           **self.local_conf)
        result = rr(req)
        self.assertEqual(result, "cat_filter")

    def test_call_to_mutt_role(self):
        context = mock.Mock()
        context.roles = ["mutt"]

        req = mock.Mock()
        req.environ = {"nova.context": context}

        rr = rolerouter.RoleRouter.factory(self.loader, self.global_conf,
                                           **self.local_conf)
        result = rr(req)
        self.assertEqual(result, "dog_filter")

    def test_call_to_untracked_role(self):
        context = mock.Mock()
        context.roles = ["blah"]

        req = mock.Mock()
        req.environ = {"nova.context": context}

        rr = rolerouter.RoleRouter.factory(self.loader, self.global_conf,
                                           **self.local_conf)
        result = rr(req)

        #NOTE(jmeridth/roaet): this needs to be called explicitly because
        # it doesn't get called in the filter chain
        self.assertEqual(result(), "appx")

    def test_multiple_roles_from_same_route(self):
        context = mock.Mock()
        context.roles = ["domestic", "outdoor"]

        req = mock.Mock()
        req.environ = {"nova.context": context}

        rr = rolerouter.RoleRouter.factory(self.loader, self.global_conf,
                                           **self.local_conf)
        result = rr(req)
        self.assertEqual(result, "cat_filter")

    def test_multiple_roles_from_different_routes_uses_first_role(self):
        context = mock.Mock()
        context.roles = ["domestic", "mutt"]

        req = mock.Mock()
        req.environ = {"nova.context": context}

        rr = rolerouter.RoleRouter.factory(self.loader, self.global_conf,
                                           **self.local_conf)
        result = rr(req)
        self.assertEqual(result, "cat_filter")

    def test_multiple_roles_from_different_routes_in_different_order(self):
        """Should use first route apps and filters for route listed in
        local_conf (in setup above) no matter order in context.roles
        """
        context = mock.Mock()
        context.roles = ["mutt", "domestic"]

        req = mock.Mock()
        req.environ = {"nova.context": context}

        rr = rolerouter.RoleRouter.factory(self.loader, self.global_conf,
                                           **self.local_conf)
        result = rr(req)
        self.assertEqual(result, "cat_filter")
