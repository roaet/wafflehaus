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
from wafflehaus.base import WafflehausBase
from wafflehaus import tests


class TestWafflehausBase(tests.TestCase):

    def test_create_default_instance(self):
        base = WafflehausBase(self.app, {})
        self.assertIsNotNone(base)
        self.assertFalse(base.testing)
        self.assertEqual(base.app, self.app)

    def test_create_default_instance_with_testing(self):
        for testing in (True, 'True', 'true', 't', '1', 'on', 'yes', 'y'):
            base = WafflehausBase(self.app, {'testing': testing})
            self.assertIsNotNone(base)
            self.assertTrue(base.testing)
            self.assertEqual(base.app, self.app)

    def test_create_default_instance_is_not_enabled(self):
        base = WafflehausBase(self.app, {})
        self.assertIsNotNone(base)
        self.assertEqual(base.app, self.app)
        self.assertFalse(base.enabled)

    def test_create_default_instance_configured_enabled(self):
        for enabled in (True, 'True', 'true', 't', '1', 'on', 'yes', 'y'):
            base = WafflehausBase(self.app, {'enabled': enabled})
            self.assertIsNotNone(base)
            self.assertEqual(base.app, self.app)
            self.assertTrue(base.enabled)

    def test_handle_header_override_called_when_configured(self):
        self.set_reconfigure()
        oc_path = 'wafflehaus.base.WafflehausBase._override'
        m_override_caller = self.create_patch(oc_path)
        base = WafflehausBase(self.app, {})
        base.__call__(None)
        self.assertTrue(m_override_caller.called)

    def test_handle_header_override_not_called_when_not_configured(self):
        oc_path = 'wafflehaus.base.WafflehausBase._override'
        m_override_caller = self.create_patch(oc_path)
        base = WafflehausBase(self.app, {})
        base.__call__(None)
        self.assertFalse(m_override_caller.called)
