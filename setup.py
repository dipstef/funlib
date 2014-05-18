from distutils.core import setup

VERSION = '0.1'

desc = """Collection of function classes and decorators"""

name = 'funlib'

setup(name=name,
      version=VERSION,
      author='Stefano Dipierro',
      author_email='dipstef@github.com',
      url='http://github.com/dipstef/{}/'.format(name),
      description=desc,
      license='http://www.apache.org/licenses/LICENSE-2.0',
      packages=[name],
      platforms=['Any'],
      requires=['unicoder']
)