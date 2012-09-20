from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='wafflehaus',
      version=version,
      description="A collection of middlewarez for nova",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Justin Hammond',
      author_email='justin.hammond@rackspace.com',
      url='https://github.rackspace.com/O3eng/wafflehaus',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
