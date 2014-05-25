===============
Resouce Filters
===============

Block Resource Middleware
-------------------------

The block resource middleware simply will return with an HTTPForbidden for any
matching resource. The matching resource is defined using the routes format.
More about the routes format and routes itself can be found
[here](http://routes.readthedocs.org/).

Use Case
~~~~~~~~

You wish to block certain methods to a resource. This works exceptionally well
when using the role router to prevent access based on user's role.

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
