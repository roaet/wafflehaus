# Copyright 2016 Openstack Foundation
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

from wafflehaus.pagination import pagination
from wafflehaus import tests


class TestPagination(tests.TestCase):
    def setUp(self):
        super(TestPagination, self).setUp()
        self.url = 'http://rewritten_url:1337'

    def test_paginate_networks(self):
        """Tests handling pagination url on networks request"""
        body = {
            "networks": [
                {"id": "XXX", "name": "name1"}],
            "networks_links": [
                {
                    "href": ("http://localhost:9696/v2.0/networks?"
                             "limit=1&marker=xxx"),
                    "rel": "next"},
                {
                    "href": ("http://localhost:9696/v2.0/networks?limit="
                             "1&marker=xxx&page_reverse=True"),
                    "rel": "previous"}
            ]
        }

        result = {
            "networks": [
                {"id": "XXX", "name": "name1"}],
            "networks_links": [
                {
                    "href": ("{}/v2.0/networks?limit=1&marker="
                             "xxx".format(self.url)),
                    "rel": "next"
                },
                {
                    "href": ("{}/v2.0/networks?limit=1&marker"
                             "=xxx&page_reverse="
                             "True".format(self.url)),
                    "rel": "previous"
                }
            ]
        }

        @webob.dec.wsgify
        def app(req):
            return webob.Response(body=json.dumps(body), status=200)
        conf = {'pagination_url': self.url, 'enabled': 'True'}
        test_filter = pagination.filter_factory(conf)(app)
        resp = test_filter(webob.Request.blank("/networks?limit=1",
                                               method="GET"))

        self.assertEqual(resp.json, result)

    def test_paginate_security_groups(self):
        """Tests handling pagination url on security-groups request"""
        body = {
            "security_groups":
            [
                {
                    "description": "",
                    "id": "XXX",
                    "name": "aq-test-1",
                    "security_group_rules": [
                        {
                            "direction": "ingress",
                            "ethertype": "IPv4",
                            "id": "XXX",
                            "port_range_max": None,
                            "port_range_min": None,
                            "protocol": "ICMP",
                            "remote_group_id": None,
                            "remote_ip_prefix": None,
                            "security_group_id": "DDD",
                            "tenant_id": "TTT"
                        },
                        {
                            "direction": "ingress",
                            "ethertype": "IPv4",
                            "id": "XXX",
                            "port_range_max": 8080,
                            "port_range_min": 8080,
                            "protocol": "TCP",
                            "remote_group_id": None,
                            "remote_ip_prefix": None,
                            "security_group_id": "DDDD",
                            "tenant_id": "TTT"
                        }
                    ],
                    "tenant_id": "TTT"
                },
                {
                    "description": "",
                    "id": "XXX",
                    "name": "name2",
                    "security_group_rules": [],
                    "tenant_id": "TTT"
                }
            ],
            "security_groups_links": [
                {
                    "href": ("https://neutron.ohthree.com:7575/v2.0/"
                             "security-groups?limit=5&marker=xxx"),
                    "rel": "next"
                },
                {
                    "href": ("https://neutron.ohthree.com:7575/v2.0/"
                             "security-groups?limit=5&marker="
                             "xxx&page_reverse=True"),
                    "rel": "previous"
                }
            ]
        }

        result = {
            "security_groups":
            [
                {
                    "description": "",
                    "id": "XXX",
                    "name": "aq-test-1",
                    "security_group_rules": [
                        {
                            "direction": "ingress",
                            "ethertype": "IPv4",
                            "id": "XXX",
                            "port_range_max": None,
                            "port_range_min": None,
                            "protocol": "ICMP",
                            "remote_group_id": None,
                            "remote_ip_prefix": None,
                            "security_group_id": "DDD",
                            "tenant_id": "TTT"
                        },
                        {
                            "direction": "ingress",
                            "ethertype": "IPv4",
                            "id": "XXX",
                            "port_range_max": 8080,
                            "port_range_min": 8080,
                            "protocol": "TCP",
                            "remote_group_id": None,
                            "remote_ip_prefix": None,
                            "security_group_id": "DDDD",
                            "tenant_id": "TTT"
                        }
                    ],
                    "tenant_id": "TTT"
                },
                {
                    "description": "",
                    "id": "XXX",
                    "name": "name2",
                    "security_group_rules": [],
                    "tenant_id": "TTT"
                }
            ],
            "security_groups_links": [
                {
                    "href": ("{}/v2.0/security-groups?limit=5&marker="
                             "xxx".format(self.url)),
                    "rel": "next"
                },
                {
                    "href": ("{}/v2.0/security-groups?limit=5&marker"
                             "=xxx&page_reverse=True".format(self.url)),
                    "rel": "previous"
                }
            ]
        }

        @webob.dec.wsgify
        def app(req):
            return webob.Response(body=json.dumps(body), status=200)

        conf = {'pagination_url': self.url, 'enabled': 'True'}
        test_filter = pagination.filter_factory(conf)(app)
        resp = test_filter(webob.Request.blank("/security-groups?limit=2",
                                               method="GET"))

        self.assertEqual(resp.json, result)

    def test_paginate_subnets(self):
        """Tests handling pagination url on subnets request"""
        body = {
            "subnets": [
                {
                    "allocation_pools": [
                        {
                            "end": "255.255.255.255",
                            "start": "0.0.0.0"
                        }
                    ],
                    "cidr": "0.0.0.0/0",
                    "dns_nameservers": [],
                    "enable_dhcp": None,
                    "gateway_ip": None,
                    "host_routes": [],
                    "id": "XXX",
                    "ip_version": None,
                    "name": "public_v4",
                    "network_id": "ZZZ",
                    "tenant_id": "TTT"
                }
            ],
            "subnets_links": [
                {
                    "href": ("https://neutron.ohthree.com:7575/v2.0/subnets?"
                             "limit=1&marker=00000000-0000-0000-0000-"
                             "000000000000"),
                    "rel": "next"
                },
                {
                    "href": ("https://neutron.ohthree.com:7575/v2.0/subnets?"
                             "limit=1&marker=00000000-0000-0000-0000-0000000"
                             "00000&page_reverse=True"),
                    "rel": "previous"
                }
            ]
        }

        result = {
            "subnets": [
                {
                    "allocation_pools": [
                        {
                            "end": "255.255.255.255",
                            "start": "0.0.0.0"
                        }
                    ],
                    "cidr": "0.0.0.0/0",
                    "dns_nameservers": [],
                    "enable_dhcp": None,
                    "gateway_ip": None,
                    "host_routes": [],
                    "id": "XXX",
                    "ip_version": None,
                    "name": "public_v4",
                    "network_id": "ZZZ",
                    "tenant_id": "TTT"
                }
            ],
            "subnets_links": [
                {
                    "href": ("{}/v2.0/subnets?limit=1&marker=00000000"
                             "-0000-0000-0000-000000000000".format(self.url)),
                    "rel": "next"
                },
                {
                    "href": ("{}/v2.0/subnets?limit=1&marker=00000000"
                             "-0000-0000-0000-000000000000&page_rever"
                             "se=True".format(self.url)),
                    "rel": "previous"
                }
            ]
        }

        @webob.dec.wsgify
        def app(req):
            return webob.Response(body=json.dumps(body), status=200)
        conf = {'pagination_url': self.url, 'enabled': 'True'}
        test_filter = pagination.filter_factory(conf)(app)
        resp = test_filter(webob.Request.blank("/subnets?limit=1",
                                               method="GET"))

        self.assertEqual(resp.json, result)

    def test_paginate_ports(self):
        """Tests handling pagination url on ports request"""
        body = {
            "ports": [
                {
                    "admin_state_up": True,
                    "bridge": "publicnet",
                    "device_id": "YYY",
                    "device_owner": "compute:None",
                    "fixed_ips": [
                        {
                            "enabled": True,
                            "ip_address": "2.2.2.2",
                            "subnet_id": "public_v4"
                        },
                        {
                            "enabled": True,
                            "ip_address": "2.2.2.2",
                            "subnet_id": "public_v6"
                        }
                    ],
                    "id": "XXX",
                    "mac_address": "02:00:03:00:00:A1",
                    "name": "",
                    "network_id": "ZZZ",
                    "security_groups": [],
                    "status": "ACTIVE",
                    "tenant_id": "TTT"
                }
            ],
            "ports_links": [
                {
                    "href": ("https://neutron.ohthree.com:7575/v2.0/ports?"
                             "limit=1&marker=xxx"),
                    "rel": "next"
                },
                {
                    "href": ("https://neutron.ohthree.com:7575/v2.0/ports?"
                             "limit=1&marker=xxx&page_reverse=True"),
                    "rel": "previous"
                }
            ]
        }

        result = {
            "ports": [
                {
                    "admin_state_up": True,
                    "bridge": "publicnet",
                    "device_id": "YYY",
                    "device_owner": "compute:None",
                    "fixed_ips": [
                        {
                            "enabled": True,
                            "ip_address": "2.2.2.2",
                            "subnet_id": "public_v4"
                        },
                        {
                            "enabled": True,
                            "ip_address": "2.2.2.2",
                            "subnet_id": "public_v6"
                        }
                    ],
                    "id": "XXX",
                    "mac_address": "02:00:03:00:00:A1",
                    "name": "",
                    "network_id": "ZZZ",
                    "security_groups": [],
                    "status": "ACTIVE",
                    "tenant_id": "TTT"
                }
            ],
            "ports_links": [
                {
                    "href": ("{}/v2.0/ports?limit=1&marker"
                             "=xxx".format(self.url)),
                    "rel": "next"
                },
                {
                    "href": ("{}/v2.0/ports?limit=1&marker=xxx"
                             "&page_reverse=True".format(self.url)),
                    "rel": "previous"
                }
            ]
        }

        @webob.dec.wsgify
        def app(req):
            return webob.Response(body=json.dumps(body), status=200)
        conf = {'pagination_url': self.url, 'enabled': 'True'}
        test_filter = pagination.filter_factory(conf)(app)
        resp = test_filter(webob.Request.blank("/ports?limit=1",
                                               method="GET"))

        self.assertEqual(resp.json, result)

    def test_paginate_non_200_response(self):
        """Tests graceful return when app response was an error"""
        body = {"does": "not", "matter": "here"}

        @webob.dec.wsgify
        def app(req):
            return webob.Response(body=json.dumps(body), status=400)
        conf = {'pagination_url': self.url, 'enabled': 'True'}
        test_filter = pagination.filter_factory(conf)(app)
        resp = test_filter(webob.Request.blank("/networks?limit=1",
                                               method="GET"))

        # Should just return our app function here, not a response with json
        self.assertEqual(resp, app)

    def test_paginate_disabled_waffle(self):
        """When pagination waffle is disabled return result as is"""
        body = {"does": "not", "matter": "here"}

        @webob.dec.wsgify
        def app(req):
            return webob.Response(body=json.dumps(body), status=200)

        conf = {'pagination_url': self.url, 'enabled': 'False'}
        test_filter = pagination.filter_factory(conf)(app)
        resp = test_filter(webob.Request.blank("/networks?limit=1",
                                               method="GET"))

        # Should just return our app function here, not a response with json
        self.assertEqual(resp, app)

    def test_paginate_missing_pagination_url(self):
        """Tests graceful exit when the pagination_url is not set in config"""
        body = {
            "networks": [
                {"id": "XXX", "name": "name1"}],
            "networks_links": [
                {
                    "href": ("http://localhost:9696/v2.0/networks?limit="
                             "1&marker=xxx"),
                    "rel": "next"
                },
                {
                    "href": ("http://localhost:9696/v2.0/networks?limit="
                             "1&marker=xxx&page_reverse=True"),
                    "rel": "previous"
                }
            ]
        }

        @webob.dec.wsgify
        def app(req):
            return webob.Response(body=json.dumps(body), status=200)

        conf = {'enabled': 'True'}
        test_filter = pagination.filter_factory(conf)(app)
        resp = test_filter(webob.Request.blank("/networks?limit=1",
                                               method="GET"))

        # Should just return our app function here, not a response with json
        self.assertEqual(resp, app)

    def test_paginate_empty_response(self):
        """Tests when the app returns None"""
        @webob.dec.wsgify
        def app(req):
            return None

        conf = {'pagination_url': self.url, 'enabled': 'True'}
        test_filter = pagination.filter_factory(conf)(app)
        resp = test_filter(webob.Request.blank("/networks?limit=1",
                                               method="GET"))

        # Should just return our app function here, not a response with json
        self.assertEqual(resp, app)

    def test_paginate_exception_response(self):
        """Tests when the app throws an Exception"""

        @webob.dec.wsgify
        def app(req):
            raise Exception

        conf = {'pagination_url': self.url, 'enabled': 'True'}
        test_filter = pagination.filter_factory(conf)(app)
        resp = test_filter(webob.Request.blank("/networks?limit=1",
                                               method="GET"))

        # Should just return our app function here, not a response with json
        self.assertEqual(resp, app)
