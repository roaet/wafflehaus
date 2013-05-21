==========
Wafflehaus
==========

Wafflehaus is a collection of WSGI middleware for nova that intends on adding functionality with minimal impact to code. The WSGI middleware that has been implemented within the wafflehaus collection should be placed into separate sections below.

Purpose
=======
Wafflehaus was created to support the specialized requirement that a certain network must be listed as a requested network during a 'create server' event if and only if the tenant in question is of a particular role. Multiple solutions were suggested but the middleware approach was selected due to low impact to code and the increased flexibility provided by adding logic to the WSGI path (implemented through Role Router).

Middleware Included with Wafflehaus
===================================

Role Router
-----------

The Role Router middleware analyzes the role in the keystone context. Because of this dependence this middleware must be after the keystonecontext filter. This middleware makes a decision based on the role and routes the request to the appropriate WSGI stack. Routes and roles are defined in the the paste.ini and can be customized without code modification. It is necessary though to restart the WSGI service that consumes the paste.ini after changes.


Role Router Configuration and Definitions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Route
        a WSGI stack that the role router will select that is a list of filters followed by an app
    Roles
        a role value that is expected to be produced by the keystone context middleware. It is important that roles between routes are mutually exclusive, stack selection of overlaping roles is indeterminate, it is determined by the order roles are added to the paste config (ie, don't try to have overlapping roles/routes, it may or may not work depending on how its configured).

The following sample paste.ini, created to support routing to different pipelines based on if a customer is of a particular role, will be used during the explanation of configuration (line-numbers on the left for clarity):

Role Router consumption::

    1  [composite:openstack_compute_api_v2]
    2  use = call:nova.api.auth:pipeline_factory
    3  keystone = faultwrap sizelimit authtoken keystonecontext ratelimit rolerouter

The important aspect of this configuration to consume the Role Router middleware is on line 3. The paste pipeline's app is set to rolerouter (which is the label set in the next section).
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

* The section header on line 1 is required by paste and defines the label that will be used when referencing the Role Router middleware.
* The use setting on line 2 will select the package and function to use when the WSGI stack reaches this point. This line is required by paste.
* The routes setting on line 4 is required and will describe the variety of routes that the role router is concerned with. It is important that the default route not be included in this descriptive list. The spelling and capitalization of these labels are important (pro-tip: keep it lowercase). This setting is required even if it is empty (pro-tip: if it is empty you shouldn't be using role router)
* The roles_managed setting on line 6 is peculiar as the ``roles_`` portion is required and standard but the ``managed`` portion must be exactly the same as a route described above. This particular setting describes the roles, simple strings, expected for the managed route. If any of the roles listed here are detected in the keystone context the router will select the corresponding ``route_`` pipeline, in this case route_managed
* The route_managed setting on line 7 is similar to the line described above (line 6). What is expected here is a list of filters followed by an app. It is possible that the app be another composite, and even another role router.
* The route_default on line 9 is the pipeline selected by the role router if none of the roles were matched. This setting is required

Request Networks
----------------

The Request Networks middleware will analyze the body of a "create server" request to nova (POST) and search for network UUIDs. This middleware will not execute for any other request. If a network UUID that is listed in the required_nets configuration (in the paste.ini) is missing from the request body this middleware will raise an HTTP Forbidden error. In addition to being able to find required networks, the Request Networks middleware can locate blacklisted networks and will raise an HTTP Forbidden error if the networks are present in the request.

Request Networks Configuration and Definitions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Network
        a UUID of a network that is required to be present or missing in the body of a "create server" request

The following sample paste.ini will be used during the explanation of configuration (line-numbers on the left for clarity):

Request Networks consumption::

    1  route_managed = requestnetworks osapi_compute_app_v2

Request Networks setup::

    1  [filter:requestnetworks]
    2  paste.filter_factory = wafflehaus.requestnetworks:RequestNetworks.factory
    3  required_nets = 00000000-0000-0000-0000-000000000000
    4                  11111111-1111-1111-1111-111111111111
    5  banned_nets = 22222222-2222-2222-2222-222222222222
    6                33333333-3333-3333-3333-333333333333

* The section header on line 1 is required by paste and defines the label that will be used when referencing the Request Networks middleware.
* The use setting on line 2 will select the package and function to use when the WSGI stack reaches this point. This line is required by paste.
* The required_nets settings on lines 3 and 4 is a list of required UUIDs to look for
* The banned_nets settings on lines 5 and 6 is a list of required UUIDs to block
* The UUIDs are just examples.

Detach Network Check
--------------------

The Detach Network Check middleware will ensure that the VIF being removed from an instance is not the interface that is attached to a particular network. This check is a little more complicated than just ensuring that a 'network' is present because the relationship between a VIF and a particular network is not immediately available. A request to a different service is necessary to look up the network information on the VIF.

Detach Network Check Configuration and Definitions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Network
        a UUID of a network that is required and cannot be detached

The following sample paste.ini will be used during the explanation of configuration (line-numbers on the left for clarity):

Detach Network Check consumption::

    1  route_managed = detachcheck osapi_compute_app_v2

Detach Network Check setup::

    1  [filter:detachcheck]
    2  paste.filter_factory = wafflehaus.detach_network_check:DetachNetworkCheck.factory
    3  required_nets = 11111111-1111-1111-1111-111111111111

* The section header on line 1 is required by paste and defines the label that will be used when referencing the Request Networks middleware.
* The use setting on line 2 will select the package and function to use when the WSGI stack reaches this point. This line is required by paste.
* The required_nets settings on lines 3 is the UUID of the network that cannot be detached

Network Count Check
-------------------

The Network Count Check middleware verifies only a certain number of networks are allowed to attach to a server. The middleware enforces this both from the body of a "create server" request to nova (POST) as well as a VIF attach request to nova (POST). This middleware will not execute for any other request. It also supports optional, required and banned network functionality and the ability to include/exclude optional networks from the count. A minimum and maximum network count can be configured to ensure the number of isolated networks being attached is within a given range, or min and max can be set to the same value to ensure a specific number of attached networks. Similar to the Request Networks functionality, if a network UUID that is listed in the required_nets configuration (in the paste.ini) is missing from the request body this middleware will raise an HTTP Forbidden error. In addition to being able to find required networks, the Network Count Check middleware can locate blacklisted networks and will raise an HTTP Forbidden error if the networks are present in the request.

Network Count Check Configuration and Definitions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Network
        a UUID of a network that is required to be present or missing in the body of a "create server" request or a network attach request

The following sample paste.ini will be used during the explanation of configuration (line-numbers on the left for clarity):

Network Count Check consumption::

    1  route_managed = network_count_check osapi_compute_app_v2

Network Count Check setup::

    1  [filter:network_count_check]
    2  paste.filter_factory = wafflehaus.network_count_check:NetworkCountCheck.factory
    3  optional_nets = 00000000-0000-0000-0000-000000000000
    4                  11111111-1111-1111-1111-111111111111
    5  required_nets = 22222222-2222-2222-2222-222222222222
    6                  33333333-3333-3333-3333-333333333333
    7  banned_nets = 44444444-4444-4444-4444-444444444444
    8                55555555-5555-5555-5555-555555555555
    9  networks_min  = 1
    10 networks_max  = 5
    11 count_optional_nets = False

* The section header on line 1 is required by paste and defines the label that will be used when referencing the Network Count Check middleware.
* The use setting on line 2 will select the package and function to use when the WSGI stack reaches this point. This line is required by paste.
* The optional_nets settings on lines 3 and 4 is a list of required UUIDs to look for. Optional setting, defaults to none.
* The required_nets settings on lines 5 and 6 is a list of required UUIDs to look for. Optional setting, defaults to none.
* The banned_nets settings on lines 7 and 8 is a list of required UUIDs to block. Optional setting, defaults to none.
* The UUIDs are just examples.
* The networks_min is the minimum number of isolated networks a server must have, enforced on server boot and VIF attach requests. Defaults to 1.
* The networks_max is the maximum number of isolated networks a server must have, enforced on server boot and VIF attach requests. Defaults to 1.
* The count_optional_nets indicates whether or not to include optional networks in the network count. For example, if you have network X as optional and have a maximum of 1 isolated network configured, a request with two networks would pass if one of them was network X (and count_optional_nets was set to False). Optional setting, defaults to False. 

Having the same middleware listed multiple times
================================================
It is possible to have a two different routes that require the same middleware but with different configurations.

The example paste.ini for this is::

    1  [composite:rolerouter]
    2  use = call:wafflehaus.rolerouter:rolerouter_factory
    3  # LIST PIPELINES TO ROUTE
    4  routes = managed special
    5  # ROLES AND ROUTES FOR MANAGED PIPELINE
    6  roles_managed = role1 role2
    7  route_managed = requestnetworks osapi_compute_app_v2
    8  roles_special = specialrole
    9  route_special = requestnetworks_special osapi_compute_app_v2
    10 # DEFAULT PIPELINE:
    11 route_default = osapi_compute_app_v2
    12 [filter:requestnetworks]
    13 paste.filter_factory = wafflehaus.requestnetworks:RequestNetworks.factory
    14 required_nets = 00000000-0000-0000-0000-000000000000
    15
    16 [filter:requestnetworks_special]
    17 paste.filter_factory = wafflehaus.requestnetworks:RequestNetworks.factory
    18 required_nets = 11111111-1111-1111-1111-111111111111
    19 banned_nets = 22222222-2222-2222-2222-222222222222

Note that the two requestnetworks targets have the same paste.filter_factory, but different parameters.
