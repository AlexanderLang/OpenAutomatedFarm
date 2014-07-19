import os

from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'pyramid',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'pyramid_layout',
    'pyramid_tm',
    'pyramid_redis'
    'SQLAlchemy',
    'transaction',
    'zope.sqlalchemy',
    'waitress',
    'mysql-connector-python',
    'deform_bootstrap',
    ]

setup(name='FarmGUI',
      version='0.1',
      description='FarmGUI',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Alexander Lang',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='farmgui',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = farmgui:main
      [console_scripts]
      initialize_FarmGUI_db = farmgui.scripts.initializedb:main
      """,
      )
