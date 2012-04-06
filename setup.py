from setuptools import setup

setup(name='Guacamole',
      version='0.1',
      description='In-memory caching for rarely-modified django models.',
      author='Chris Stucchio',
      author_email='stucchio@gmail.com',
      url='https://github.com/stucchio/Guacamole',
      packages = ['guacamole'],
      package_dir= { 'guacamole' : 'guacamole' },
      install_requires=['django'],
     )
