<h1>Wafflehaus</h1>
<p>
Wafflehaus is a collection of WSGI middleware for nova that intends on adding functionality with minimal impact to code. The WSGI middleware that has been implemented within the wafflehaus collection should be placed into separate sections below.
</p>

<h2>Purpose:</h2>
<p>
Wafflehaus was created to support the specialized requirement that the service-net must be listed as a requested network during a 'create server' event if and only if the tenant in question is a managed or rack-connect customer. Multiple solutions were suggested but the middleware approach was selected due to low impact to code and the increased flexibility provided by adding logic to the WSGI path (implemented through Role Router).
</p>

<h2>Middleware Included with Wafflehaus</h2>
<h3>Role Router</h3>
<p>
The Role Router middleware analyzes the role in the keystone context. Because of this dependence this middleware must be after the keystonecontext filter. This middleware makes a decision based on the role and routes the request to the appropriate WSGI stack. Routes and roles are defined in the the paste.ini and can be customized without code modification. It is necessary though to restart the WSGI service that consumes the paste.ini after changes.
</p>

<h3>Role Router Configuration and Definitions</h3>
<ul>
<li>
Route: a WSGI stack that the role router will select that is a list of filters followed by an app
</li>
<li>
Roles: a role value that is expected to be produced by the keystone context middleware. It is important that roles between routes are mutually exclusive, stack selection of overlaping roles is indeterminate, it is determined by the order roles are added to the paste config (ie, don't try to have overlapping roles/routes, it may or may not work depending on how its configured).
</li>
</ul>
<p>
The following sample paste.ini, created to support routing to different pipelines based on if a customer is managed or rack-connect, will be used during the explanation of configuration (line-numbers on the left for clarity):
</p>
<h3>
Role Router consumption:
</h3>
<pre>
1  [composite:openstack_compute_api_v2]
2  use = call:nova.api.auth:pipeline_factory
3  keystone = faultwrap sizelimit authtoken keystonecontext ratelimit rolerouter
</pre>
<p>
The important aspect of this configuration to consume the Role Router middleware is on line 3. The paste pipeline's app is set to rolerouter (which is the label set in the next section).
</p>
<h3>
Role Router setup:
</h3>
<pre>
1  [composite:rolerouter]
2  use = call:wafflehaus.rolerouter:rolerouter_factory
3  # LIST PIPELINES TO ROUTE
4  routes = managed
5  # ROLES AND ROUTES FOR MANAGED PIPELINE
6  roles_managed = rax_managed rack_connect
7  route_managed = requestnetworks osapi_compute_app_v2
8  # DEFAULT PIPELINE:
9  route_default = osapi_compute_app_v2
</pre>
<p>
The section header on line 1 is required by paste and defines the label that will be used when referencing the Role Router middleware.<br/>
The use setting on line 2 will select the package and function to use when the WSGI stack reaches this point. This line is required by paste.<br/>
The routes setting on line 4 is required and will describe the variety of routes that the role router is concerned with. It is important that the default route not be included in this descriptive list. The spelling and capitalization of these labels are important (pro-tip: keep it lowercase). This setting is required even if it is empty (pro-tip: if it is empty you shouldn't be using role router)<br/>
The roles_managed setting on line 6 is peculiar as the "roles_" portion is required and standard but the "managed" portion must be exactly the same as a route described above. This particular setting describes the roles, simple strings, expected for the managed route. If any of the roles listed here are detected in the keystone context the router will select the corresponding route_ pipeline, in this case route_managed<br/>
The route_managed setting on line 7 is similar to the line described above (line 6). What is expected here is a list of filters followed by an app. It is possible that the app be another composite, and even another role router.<br/>
The route_default on line 9 is the pipeline selected by the role router if none of the roles were matched. This setting is required<br/>
</p>
<h2>
Request Networks
</h2>
<p>
The Request Networks middleware will analyze the body of a "create server" request to nova (POST) and search for network UUIDs. This middleware will not execute for any other request. If a network UUID that is listed in the required_nets configuration (in the paste.ini) is missing from the request body this middleware will raise an HTTP Forbidden error. In addition to being able to find required networks, the Request Networks middleware can locate blacklisted networks and will raise an HTTP Forbidden error if the networks are present in the request.
</p>
<h3>
Request Networks Configuration and Definitions
</h3>
<ul>
<li>
Network: a UUID of a network that is required to be present or missing in the body of a "create server" request
</li>
</ul>
<p>
 The following sample paste.ini will be used during the explanation of configuration (line-numbers on the left for clarity):
</p>
<h3>
Request Networks consumption:
</h3>
<pre>
1  route_managed = requestnetworks osapi_compute_app_v2
Request Networks setup:

1  [filter:requestnetworks]
2  paste.filter_factory = wafflehaus.requestnetworks:RequestNetworks.factory
3  required_nets = 00000000-0000-0000-0000-000000000000
4                  11111111-1111-1111-1111-111111111111
5  banned_nets = 22222222-2222-2222-2222-222222222222
6                33333333-3333-3333-3333-333333333333
 </pre>
<p>

The section header on line 1 is required by paste and defines the label that will be used when referencing the Request Networks middleware.
The use setting on line 2 will select the package and function to use when the WSGI stack reaches this point. This line is required by paste.
The required_nets settings on lines 3 and 4 is a list of required UUIDs to look for
The banned_nets settings on lines 5 and 6 is a list of required UUIDs to block
</p>
