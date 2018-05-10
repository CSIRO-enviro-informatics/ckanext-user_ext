# -*- coding: utf-8 -*-
# Always prefer setuptools over distutils
import setuptools
from setuptools import setup, find_packages
from codecs import open  # To use a consistent encoding
from os import path
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
st_vers = setuptools.__version__
log.info("Using setuptools v{}".format(str(st_vers)))
try:
    try:
        import packaging # direct use
    except ImportError:
        # v39.0 and above.
        try:
            from setuptools.extern import packaging
        except ImportError:
            from pkg_resources.extern import packaging
    version = packaging.version
except ImportError:
    raise RuntimeError("The 'packaging' library is missing.")


try:
    import ckan
    from ckan.plugins import toolkit
except ImportError as e:
    raise RuntimeError("CKAN must be installed before this plugin.")

try:
    import sqlalchemy
except ImportError as e:
    raise RuntimeError("SQLAlchemy should have been installed with CKAN.")
sa_vers = version.parse(sqlalchemy.__version__)
log.info("Found SQLAlchemy {} ...".format(str(sa_vers)))
min_sa_vers = version.parse("0.9.6")
max_sa_vers = version.parse("1.1.11")
if sa_vers < min_sa_vers:
    raise RuntimeError(
        "Version of SQLAlchemy must be >= {}".format(str(min_sa_vers)))
if sa_vers > max_sa_vers:
    raise RuntimeError(
        "Version of SQLAlchemy must be <= {}".format(str(max_sa_vers)))

try:
    import migrate
except ImportError as e:
    raise RuntimeError(
        "SQLAlchemy-migrate should have been installed with CKAN.")

sm_vers = version.parse(migrate.__version__)
log.info("Found SQLAlchemy-Migrate {} ...".format(str(sm_vers)))
min_sm_vers = version.parse("0.10.0")
max_sm_vers = version.parse("0.10.0")
if sm_vers < min_sa_vers:
    raise RuntimeError(
        "Version of SQLAlchemy-migrate must be >= {}".format(str(min_sm_vers)))
if sm_vers > max_sa_vers:
    raise RuntimeError(
        "Version of SQLAlchemy-migrate must be <= {}".format(str(max_sm_vers)))

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='''ckanext-user_ext''',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # http://packaging.python.org/en/latest/tutorial.html#version
    version='0.1.0',

    description='''An extensible additional user table,
     for other plugins to use''',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/CSIRO-enviro-informatics/ckanext-user_ext',

    # Author details
    author='''Ashley Sommer''',
    author_email='''ashley.sommer@csiro.au''',

    # Choose your license
    license='AGPL',  # Cannot change this licence!

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        # 3 - Alpha
        # 4 - Beta
        # 5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: '
        'GNU Affero General Public License v3 or later (AGPLv3+)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
        # Grumble not python3 compatible.
    ],


    # What does your project relate to?
    keywords='''CKAN user table extension plugin column''',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    namespace_packages=['ckanext'],

    install_requires=[
      "SQLAlchemy=={}".format(sqlalchemy.__version__),  # redundant, I know.
      "sqlalchemy-migrate=={}".format(migrate.__version__)
    ],

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    include_package_data=True,
    package_data={
    },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages.
    # see http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    data_files=[],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points='''
        [ckan.plugins]
        user_ext=ckanext.user_ext.plugin:UserExtPlugin

        [babel.extractors]
        ckan = ckan.lib.extract:extract_ckan
    ''',

    # If you are changing from the default layout of your extension, you may
    # have to change the message extractors, you can read more about babel
    # message extraction at
    # http://babel.pocoo.org/docs/messages/#extraction-method-mapping-and-configuration
    message_extractors={
        'ckanext': [
            ('**.py', 'python', None),
            ('**.js', 'javascript', None),
            ('**/templates/**.html', 'ckan', None),
        ],
    }
)
