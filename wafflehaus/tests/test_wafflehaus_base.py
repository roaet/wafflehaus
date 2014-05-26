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

from wafflehaus.base import WafflehausBase
from wafflehaus import tests


class TestWafflehausBase(tests.TestCase):
    def setUp(self):
        self.app = mock.Mock()

    def test_create_default_instance(self):
        base = WafflehausBase(self.app, {})
        self.assertIsNotNone(base)
        self.assertFalse(base.testing)
        self.assertEqual(base.app, self.app)

    def test_create_default_instance_with_testing(self):
        base = WafflehausBase(self.app, {'testing': 'true'})
        self.assertIsNotNone(base)
        self.assertTrue(base.testing)
        self.assertEqual(base.app, self.app)

    def test_create_default_instance_is_not_enabled(self):
        base = WafflehausBase(self.app, {})
        self.assertIsNotNone(base)
        self.assertEqual(base.app, self.app)
        self.assertFalse(base.enabled)

    def test_create_default_instance_configured_enabled(self):
        base = WafflehausBase(self.app, {'enabled': 'true'})
        self.assertIsNotNone(base)
        self.assertEqual(base.app, self.app)
        self.assertTrue(base.enabled)
