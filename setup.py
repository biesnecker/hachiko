import os
import sys
from distutils.core import setup

def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

if sys.version_info >= (3, 5):
    install_requires = []
else:
    install_requires = ['asyncio']

install_requires.append('watchdog')

exec(open('hachiko/version.py').read())

setup(name='hachiko',
      version=__version__,
      author='John Biesnecker',
      author_email='jbiesnecker@gmail.com',
      url='https://github.com/biesnecker/hachiko',
      packages=['hachiko'],
      package_dir={'hachiko': './hachiko'},
      install_requires=install_requires,
      description='Asyncio wrapper around watchdog.',
      license='mit',
      long_description=read('README.txt')
)