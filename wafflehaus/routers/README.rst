=======
Routers
=======

Role Router
-----------

The Role Router middleware analyzes the role in the keystone context. Because
of this dependence this middleware must be after the keystonecontext filter.
This middleware makes a decision based on the role and routes the request to
the appropriate WSGI stack. Routes and roles are defined in the the paste.ini
and can be customized without code modification. It is necessary though to
restart the WSGI service that consumes the paste.ini after changes.

Use Case 1
~~~~~~~~~~

You wish to perform additional checks (using middleware) based on the user's
role.

Use Case 2
~~~~~~~~~~

You wish to route users to different applications based on the user's role.

Role Router Configuration and Definitions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Route
        a WSGI stack that the role router will select that is a list of filters
        followed by an app
    Roles
        a role value that is expected to be produced by the keystone context
        middleware. It is important that roles between routes are mutually
        exclusive, stack selection of overlaping roles is indeterminate, it is
        determined by the order roles are added to the paste config (ie, don't
        try to have overlapping roles/routes, it may or may not work depending
        on how its configured).

The following sample paste.ini, created to support routing to different
pipelines based on if a customer is of a particular role, will be used during
the explanation of configuration (line-numbers on the left for clarity):

Role Router consumption::

    1  [composite:openstack_compute_api_v2]
    2  use = call:nova.api.auth:pipeline_factory
    3  keystone = faultwrap sizelimit authtoken keystonecontext ratelimit rolerouter

The important aspect of this configuration to consume the Role Router
middleware is on line 3. The paste pipeline's app is set to rolerouter (which
is the label set in the next section).

Role Router setup::

    1  [composite:rolerouter]
    2  use = call:wafflehaus.rolerouter:rolerouter_factory
    3  # LIST PIPELINES TO ROUTE
    4  routes = managed
    5  # ROLES AND ROUTES FOR MANAGED PIPELINE
    6  roles_managed = role1 role2
    7  route_managed = requestnetworks osapi_compute_app_v2
    8  # DEFAULT PIPELINE:
    9  route_default = osapi_compute_app_v2
    10 enabled = true

* The section header on line 1 is required by paste and defines the label that
  will be used when referencing the Role Router middleware.
* The use setting on line 2 will select the package and function to use when
  the WSGI stack reaches this point. This line is required by paste.
* The routes setting on line 4 is required and will describe the variety of
  routes that the role router is concerned with. It is important that the
  default route not be included in this descriptive list. The spelling and
  capitalization of these labels are important (pro-tip: keep it lowercase).
  This setting is required even if it is empty (pro-tip: if it is empty you
  shouldn't be using role router)
* The roles_managed setting on line 6 is peculiar as the ``roles_`` portion is
  required and standard but the ``managed`` portion must be exactly the same as
  a route described above. This particular setting describes the roles, simple
  strings, expected for the managed route. If any of the roles listed here are
  detected in the keystone context the router will select the corresponding
  ``route_`` pipeline, in this case route_managed
* The route_managed setting on line 7 is similar to the line described above
  (line 6). What is expected here, is a list of filters followed by an app. Make
  sure to order your filters in the order you want them wrapped. It is possible
  that the app be another composite, and even another role router.
* The route_default on line 9 is the pipeline selected by the role router if
  none of the roles were matched. This setting is required

Note: that prioritization of which route to use is based on the order that they
are definined, where the first route is considered first
