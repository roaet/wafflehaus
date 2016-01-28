Rest Logging
============

The rest logging filter will consume all requests and responses and output a
simplified log with no debug information.


Use-Case
~~~~~~~~

This is useful for situations where your WSGI api is very verbose and it is
difficult to understand what is going on.


Example Config
~~~~~~~~~~~~~~

A basic configuration for normal use::

    [filter:reqresplog]
    paste.filter_factory = wafflehaus.log_filters.req_resp:filter_factory
    enabled = true
    log_file = /var/log/server/simple.log
    context_key = neutron.context


Config Options
~~~~~~~~~~~~~~
- **log_file** (required): the target log file
- **context_key**: the key to look for in the context
- **detail_level**: output detailed logs if status code >= this value
- **do_detail_logs**: to output detailed logs to another file based on level
