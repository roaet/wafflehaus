import setuptools

version = '0.1'

setuptools.setup(name='wafflehaus',
    version=version,
    description="A collection of middleware for nova",
    classifiers=[
      "Development Status :: 5 - Production/Stable",
      "Environment :: Web Environment",
      "Framework :: Paste",
      "Intended Audience :: Developers",
      "Intended Audience :: Sustem Administrators",
      "License :: OSI Approved :: Apache Software License",
      "Operating System : OS Independent",
      "Programming Language :: Python :: 2.7",
      "Programming Language :: Python :: 2.6",
      "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware"
    ], 
    keywords=['openstack', 'nova'],
    author='Justin Hammond',
    author_email='justin.hammond@rackspace.com',
    url='https://github.com/roaet/wafflehaus',
    license='Apache Software License',
    packages=['wafflehaus'],
    zip_safe=False,
    install_requires=[
      "webob",
      "nova",
    ],
)
