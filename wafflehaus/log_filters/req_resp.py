# Copyright 2016 Justin Hammond
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
import logging
import time
import uuid

import webob.dec
import webob.exc

import wafflehaus.base


FAKE_REQ_ID = 'req-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX'
FAKE_TENANT_ID = '-'
DEFAULTS = {'request': FAKE_REQ_ID, 'tenant': FAKE_TENANT_ID}


class RequestResponseLogger(wafflehaus.base.WafflehausBase):

    def _get_new_log(self, name, log_file, log_format):
        formatter = logging.Formatter(log_format)
        fileHandler = logging.FileHandler(log_file)
        fileHandler.setFormatter(formatter)

        log = logging.getLogger(name)
        log.handlers = []
        log.addHandler(fileHandler)
        log.propagate = False
        return log

    def __init__(self, app, conf):
        super(RequestResponseLogger, self).__init__(app, conf)
        self.log.name = conf.get('log_name', __name__)
        self.context_key = conf.get('context_key', 'nokey')
        self.separator = ' '
        self.do_detail_logs = (conf.get('do_detail') in self.truths)
        self.detail_level = int(conf.get('detail_level', 500))
        default_format = '%(message)s' + self.separator + '%(asctime)s'
        log_format = default_format
        log_file = conf.get('log_file')

        if log_file is not None:
            self.log = self._get_new_log(self.log.name, log_file, log_format)
            self.log.info('Starting wafflehaus request/response logger')
            if self.do_detail_logs:
                dlog_file = "%s.detail.log" % log_file.replace('.log', '')
                name = "%s.details"
                self.dlog = self._get_new_log(name, dlog_file, '%(message)s')
        else:
            self.enabled = False

    def _log_simple_request(self, req, resp, delta, log_time):
        contents = []
        context_info = DEFAULTS
        ctx = req.environ.get(self.context_key)
        if ctx is not None:
            context_info['request'] = ctx.request_id
            if ctx.tenant_id is not None:
                context_info['tenant'] = ctx.tenant_id
        id = str(uuid.uuid4())
        if context_info['request'] != FAKE_REQ_ID:
            id = context_info['request']

        contents.append("%d" % resp.status_int)
        contents.append("%f sec" % delta)
        contents.append('<--')
        contents.append(req.method)
        qs = ""
        if len(req.query_string) > 0:
            qs = "?%s" % req.query_string
        contents.append("%s%s" % (req.path, qs))
        contents.append(context_info['request'])
        contents.append(context_info['tenant'])

        if self.do_detail_logs:
            contents.append(id)

        """Turn everything into a string."""
        string_contents = [str(c) for c in contents]

        log_str = self.separator.join(string_contents)
        self.log.info(log_str)
        if resp.status_int >= self.detail_level and self.do_detail_logs:
            self._log_detail_request(id, req, resp, delta, log_time)

    def _log_detail_request(self, id, req, resp, delta, log_time):
        context_info = DEFAULTS
        ctx = req.environ.get(self.context_key)
        if ctx is not None:
            context_info['request'] = ctx.request_id
            if ctx.tenant_id is not None:
                context_info['tenant'] = ctx.tenant_id
        qs = ""
        if len(req.query_string) > 0:
            qs = "?%s" % req.query_string
        self.dlog.info("%s | ---" % id)
        self.dlog.info("%s | REQTIME: %s" % (id, log_time))
        self.dlog.info("%s | REQDIFF: %f seconds" % (id, delta))
        self.dlog.info("%s | REQCALL: %s %s%s" % (id, req.method, req.path,
                                                  qs))

        if req.body and len(req.body) > 0:
            body_list = req.body.split('\n')
            for line in body_list:
                self.dlog.info("%s | REQBODY: %s" % (id, line))

        for header, value in req.headers.iteritems():
            self.dlog.info("%s | REQHEAD: %s:%s" % (id, header, value))
        self.dlog.info("%s | REQADDR: %s" % (id, req.remote_addr))

        self.dlog.info("%s | RESTEXT: %s" % (id, resp.status))
        self.dlog.info("%s | RESCODE: %s" % (id, resp.status_int))

        if resp.body and len(resp.body) > 0:
            body_list = resp.body.split('\n')
            for line in body_list:
                self.dlog.info("%s | RESBODY: %s" % (id, line))

    @webob.dec.wsgify
    def __call__(self, req):
        super(RequestResponseLogger, self).__call__(req)
        if not self.enabled:
            return self.app

        start = time.time()
        resp = req.get_response(self.app)
        difference = (time.time() - start)

        log_time = time.strftime("%Y-%m-%d %H:%M")
        try:
            self._log_simple_request(req, resp, difference, log_time)
        except Exception as e:
            self.log("Failed to log due to exception: %s" % e)

        if resp is None:
            return self.app
        else:
            return resp


def filter_factory(global_conf, **local_conf):
    """Returns a WSGI filter app for use with paste.deploy."""
    conf = global_conf.copy()
    conf.update(local_conf)

    def req_resp_logger(app):
        return RequestResponseLogger(app, conf)
    return req_resp_logger
