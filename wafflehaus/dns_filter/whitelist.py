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
"""This middleware is intended to be used with paste.deploy."""
import logging

import dns.exception
import dns.resolver
import dns.reversename

from oslo.config import cfg


CONF = cfg.CONF


if CONF is None:
    for _app in 'nova', 'glance', 'quantum', 'cinder', 'neutron':
        try:
            cfg = __import__('%s.openstack.common.cfg' % _app,
                             fromlist=['%s.openstack.common' % _app])
            if hasattr(cfg, 'CONF') and 'config_file' in cfg.CONF:
                CONF = cfg.CONF
                break
        except ImportError:
            pass
if CONF is None:
    raise ImportError("Could not import oslo.config")


CONF_OPTS = [
    cfg.StrOpt('whitelist',
               default=[],
               help='List of whitelisted strings to match the end '
                    'of PTR query responses. Ex: google.com'),
    cfg.BoolOpt('testing',
                default=False,
                help='Will put the middleware into testing mode where it will '
                     'always pass'),
    cfg.BoolOpt('negative_testing',
                default=False,
                help='Will put the middlware into testing mode where it will '
                     'always fail'),
    cfg.BoolOpt('testing_remote_addr',
                default=None,
                help='The remote addr to use while testing'),
    cfg.StrOpt('nameserver',
               default=None,
               help='The IP of a nameserver address to override OS default'),
]
CONF.register_opts(CONF_OPTS, group='dns_whitelist')


def check_reverse_dns(ip_address, a_record_rrset):
    """Checks to ensure IP is within a set of IPs from an A query set."""
    match = any(ip_address == str(val) for val in a_record_rrset)
    return match


def check_domain_to_whitelist(domain, whitelist):
    """Checks to ensure a domain ends with at least one of a whitelisted
    domain-ending string.
    """
    if domain.endswith('.'):
        domain = domain[:-1]
    for ok_host in whitelist:
        if domain.endswith(ok_host):
            return True
    return False


def response_headers(content_length):
    """Creates the default headers for all errors."""
    return [
        ("Content-type", "text/html"),
        ("Content-length", str(content_length)),
    ]


def do_403(start_response):
    """Performs a standard 403 error."""
    start_response("403 Forbidden",
                   response_headers(0))
    return ["", ]


def do_500(start_response):
    """Performs a standard 500 error."""
    start_response("500 Internal Server Error",
                   response_headers(0))
    return ["", ]

WHITELIST = None


# pylint: disable=R0903
class DNSWhitelist(object):
    """DNSWhitelist middleware will DNS lookup REMOTE_ADDR and attempt to
    match result to a whitelist. A failed match will 403.
    """

    def _conf_get(self, name, default=None):
        """Will attempt to get config from paste config first, then config of
        the service this middleware is filtering.
        """
        if name in self.conf:
            return self.conf.get(name, default)
        else:
            try:
                return CONF.wafflehaus_dns_whitelist.get(name, default)
            except AttributeError:
                return default

    def __init__(self, app, conf):
        self.conf = conf
        self.app = app
        logname = __name__
        self.log = logging.getLogger(conf.get('log_name', logname))
        self.log.info('Starting wafflehaus dns whitelist middleware')
        self.testing = (self._conf_get('testing') in
                        (True, 'true', 't', '1', 'on', 'yes', 'y'))
        self.negative_testing = (self._conf_get('negative_testing') in
                                 (True, 'true', 't', '1', 'on', 'yes', 'y'))
        self.whitelist = self._create_whitelist()
        if self.negative_testing:
            self.testing = True

    def _create_resolver(self):
        """Creates the DNS resolver."""
        nameserver = str(dns.resolver.Resolver().nameservers[0])
        nameserver = self._conf_get('nameserver', nameserver)
        res = dns.resolver.Resolver(configure=False)
        res.nameservers = [nameserver]
        return res

    def _create_whitelist(self, key='whitelist'):
        """Creates the whitelist from configuration or testing whitelists."""
        test_list = []
        if self.testing:
            if self.negative_testing:
                test_list = ['derp.com']
            test_list = ['rackspace.com']
        whitelist = self._conf_get(key, test_list)
        if isinstance(whitelist, basestring):
            whitelist = whitelist.split(" ")
        return whitelist

    def __call__(self, env, start_response):
        """Performs white listing of REMOTE_ADDR and will fail if:
            - PTR query of REMOTE_ADDR does not end with a whitelisted domain
            - A query of PTR query fails to match REMOTE_ADDR
        """
        if not self.whitelist:
            self.log.error("Whitelist not set")
            return do_500(start_response)

        remote_addr = env['REMOTE_ADDR']
        if self.testing:
            remote_addr = self._conf_get('testing_remote_addr', remote_addr)

        self.log.debug("DNS check of %s against %s" % (remote_addr,
                                                       str(self.whitelist)))

        res = self._create_resolver()

        try:
            name = dns.reversename.from_address(remote_addr)
            ptr = res.query(name, "PTR")[0]

            if not check_domain_to_whitelist(str(ptr), self.whitelist):
                self.log.warning("DNS whitelist matching failure")
                return do_403(start_response)

            a_record = res.query(str(ptr), "A")
        except dns.exception.DNSException:
            msg = "Missing DNS entries?"
            self.log.error("DNS Error during query: " + msg)
        if not self.testing:
            return do_500(start_response)
        else:
            return self.app(env, start_response)

        if not check_reverse_dns(remote_addr, a_record.rrset):
            if self.testing:
                self.log.warning("Reverse DNS check failed")
            else:
                self.log.warning("Reverse DNS check failed")
                return do_403(start_response)
        return self.app(env, start_response)


def filter_factory(global_conf, **local_conf):
    """Returns a WSGI filter app for use with paste.deploy."""
    conf = global_conf.copy()
    conf.update(local_conf)

    def auth_bypass(app):
        """Returns the app for paste.deploy."""
        return DNSWhitelist(app, conf)
    return auth_bypass
