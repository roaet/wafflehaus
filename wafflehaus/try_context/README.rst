================
Context Emulator
================

The context emulator is a middleware that will create a context for a
configured Openstack project (nova, neutron). This is useful if your
deployment of that project is not using authentication that provides a context
but your particular business logics require one to exist.

This does not provide AuthN support and will not ensure that people are who
they say they are. This middleware only provides the creation of a admin-level
context for all WSGI entities downstream.

Use Case
--------

Service-to-service communication isn't authenticated but the external service
will send keystone specific headers. This will provide support for thos headers
without requiring the use of keystone.

How it is Configured
--------------------

::

    [filter:try_context]
    paste.filter_factory = wafflehaus.try_context.context_filter:filter_factory
    # the neutron context is used as an example
    context_strategy = wafflehaus.neutron.context.neutron_context.NeutronContextFilter
    enabled = true

Each subproject will define a context if available. These context packages are
developed as needed so some may not be available yet.

Leaving context_strategy blank, or not defining it at all is a noop.

Placement in the WSGI Stack
---------------------------

This middleware should be placed before any middleware or applications that
expect a context.

::

    [composite:neutronapi_v2_0]
    use = call:neutron.auth:pipeline_factory
    someauth = upstream_middleware try_context downstream_middleware app

Possible Errors
---------------

This middleware will not produce an error unless it is inappropriately
configured. Currently the errorneous situations are:

- No strategy configured will 500 on all requests
- Incorrectly defined strategies have undefined side-effects
