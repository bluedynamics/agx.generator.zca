import os
from setuptools import (
    setup,
    find_packages,
)


version = '1.0a1'
shortdesc = "AGX generator for zope component architecture"
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
longdesc += open(os.path.join(os.path.dirname(__file__), 'LICENSE.rst')).read()


setup(name='agx.generator.zca',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Programming Language :: Python', 
      ],
      keywords='AGX, Code Generator',
      author='BlueDynamics Alliance',
      author_email='dev@bluedynamics.com',
      url=u'http://github.com/bluedynamics/agx.generator.zca',
      license='GNU General Public Licence',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['agx', 'agx.generator'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'node.ext.zcml',
          'agx.generator.pyegg',
      ],
      extras_require = dict(
          test=[
            'interlude',
          ]
      ),
      entry_points="""
      # -*- Entry points: -*-
      [agx.generator]
      register = agx.generator.zca:register
      """)
