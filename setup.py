#!/usr/bin/python
# -*- encoding: utf-8 -*-
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
import setuptools

version = '0.3.0'

setuptools.setup(
    name='wafflehaus',
    version=version,
    description="A collection of middleware for openstack",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Paste",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 2.6",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware"
    ],
    keywords=['openstack'],
    author='Justin Hammond',
    author_email='justin.hammond@rackspace.com',
    url='https://github.com/roaet/wafflehaus',
    license='Apache Software License',
    packages=setuptools.find_packages(exclude=['tests']),
    long_description=open('README.rst').read(),
    zip_safe=False,
    install_requires=[
        "webob",
    ],
    namespace_packages=['wafflehaus'],
)
