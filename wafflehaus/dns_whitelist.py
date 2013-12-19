import logging

import dns.exception
import dns.resolver
import dns.reversename

log = logging.getLogger('neutron.' + __name__)

CONF = None
for app in 'nova', 'glance', 'quantum', 'cinder':
    try:
        cfg = __import__('%s.openstack.common.cfg' % app,
                         fromlist=['%s.openstack.common' % app])
        if hasattr(cfg, 'CONF') and 'config_file' in cfg.CONF:
            CONF = cfg.CONF
            break
    except ImportError:
        pass
if not CONF:
    from oslo.config import cfg
    CONF = cfg.CONF


opts = [
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
    cfg.StrOpt('nameserver',
               default=None,
               help='The IP of a nameserver address to override OS default'),
]
CONF.register_opts(opts, group='dns_whitelist')


class DNSWhitelist(object):

    def _conf_get(self, name, default=None):
        if name in self.conf:
            return self.conf.get(name, default)
        else:
            try:
                return CONF.wafflehaus_dns_whitelist.get(name, default)
            except AttributeError:
                return default

    def __init__(self, app, conf):
        logname = "neutron." + __name__
        self.conf = conf
        self.app = app
        self.LOG = logging.getLogger(conf.get('log_name', logname))
        self.LOG.info('Starting wafflehaus dns whitelist middleware')
        self.testing = (self._conf_get('testing') in
                        (True, 'true', 't', '1', 'on', 'yes', 'y'))
        self.negative_testing = (self._conf_get('negative_testing') in
                                 (True, 'true', 't', '1', 'on', 'yes', 'y'))
        if self.negative_testing:
            self.testing = True

    def _response_headers(self, content_length):
        response_headers = [
                ("Content-type", "text/html"),
                ("Content-length", str(content_length)),
                ]
        return response_headers

    def _do_403(self, start_response):
        start_response("403 Forbidden",
                       self._response_headers(0))
        return ["",]

    def _do_500(self, start_response):
        start_response("500 Internal Server Error",
                       self._response_headers(0))
        return ["",]

    def _check_reverse_dns(self, ip, a_record_rrset):
        match = any(ip == str(val) for val in a_record_rrset)
        return match

    def _check_domain_to_whitelist(self, domain, whitelist):
        if domain.endswith('.'):
            domain = domain[:-1]
        for ok_host in whitelist:
            if domain.endswith(ok_host):
                return True
        return False

    def _create_resolver(self):
        ns = str(dns.resolver.Resolver().nameservers[0])
        ns = self._conf_get('nameserver', ns)
        res = dns.resolver.Resolver(configure=False)
        res.nameservers = [ns]
        return res

    def _create_whitelist(self, key='whitelist'):
        whitelist = self._conf_get('whitelist', [])
        if isinstance(whitelist, basestring):
            whitelist = whitelist.split(" ")
        return whitelist


    def __call__(self, env, start_response):
        whitelist = self._create_whitelist()
        if not whitelist:
            self.LOG.error("Whitelist not set")
            return self._do_500(start_response)

        remote_addr = env['REMOTE_ADDR']
        res = self._create_resolver()

        if self.testing:
            remote_addr = "98.129.20.206"
            whitelist = ['rackspace.com']
            if self.negative_testing:
                whitelist = ['derp.com']
        try:
            name = dns.reversename.from_address(remote_addr)
            ptr = res.query(name, "PTR")[0]

            if not self._check_domain_to_whitelist(str(ptr), whitelist):
                self.LOG.warning("DNS whitelist matching failure")
                return self._do_403(start_response)

            a_record = res.query(str(ptr), "A")
        except dns.exception.DNSException:
            msg = "Missing DNS entries?"
            self.LOG.error("DNS Error during query: " + msg)
            return self._do_500(start_response)

        if not self._check_reverse_dns(remote_addr, a_record.rrset):
            if self.testing:
                self.LOG.warning("Reverse DNS check failed")
            else:
                self.LOG.warning("Reverse DNS check failed")
                return self._do_403(start_response)
        return self.app(env, start_response)


def filter_factory(global_conf, **local_conf):
    """Returns a WSGI filter app for use with paste.deploy."""
    conf = global_conf.copy()
    conf.update(local_conf)

    def auth_bypass(app):
        return DNSWhitelist(app, conf)
    return auth_bypass
