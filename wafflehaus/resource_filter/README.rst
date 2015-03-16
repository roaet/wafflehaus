===============
Resouce Filters
===============

Alias Resource Middleware
-------------------------

The alias reousrce middle will either redirect (30X) a resource or return a
40X as configured. The matching resource is defined using the routes format.
More about the routes format and routes itself can be found
[here](http://routes.readthedocs.org/).

This middleware is not *method*  specific and will not detect any difference
based on *method*.

Use Case
~~~~~~~~

If a resource can't be added to your list, or if there is a bug with routes
such [as this one](https://bugs.launchpad.net/neutron/+bug/1014591) this can
be used to fix that.

Example
~~~~~~~

::

    [example 1]
    # 400s all requests /widget with friendly message
    resource = /widget
    action = 400:A trailing slash '/' is required for this resource
    enabled = true

    [example 2]
    # 301s all requests to /widget -> /cog
    resource = /widget
    action = 301:/cog
    enabled = true

    [example 3]
    # Will redirect the user to the resource with a slash added
    resource = /widget
    action = addslash
    enabled = true

    [example 4 (not implemented yet)]
    # Make a subrequest for the user making and perform the redirect
    # transparently
    resource = /widget
    action = subrequest:/cog
    enabled = true


Block Resource Middleware
-------------------------

The block resource middleware simply will return with an HTTPForbidden for any
matching resource. The matching resource is defined using the routes format.
More about the routes format and routes itself can be found
[here](http://routes.readthedocs.org/).

Use Case
~~~~~~~~

You wish to block certain methods to a resource. This works exceptionally well
when using a router to block based on some logic.

Example
~~~~~~~

::

    [example 1]
    # prevents POST to /widget
    resource = POST /widget
    enabled = true

    [example 2]
    # prevents POST and GET to /widget
    resource = POST GET /widget
    enabled = true

    [example 3]
    # prevents POST to /widget and POST and GET to /cog
    resource = POST /widget, POST GET /cog
    enabled = true

    [example 4]
    # prevents POST to a complex uri
    # it is important that the two wild cards (id, owner_id) are different
    resource = POST /widget/{id}/owner/{owner_id}
    enabled = true

    [example 5]
    # prevents POST to a complex uri with additional format options
    resource = POST /widget{.format}
    enabled = true
