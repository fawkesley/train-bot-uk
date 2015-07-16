# encoding: utf-8

from setuptools import setup, find_packages

import codecs
import os
import re


def find_version(*file_paths):
    # Open in Latin-1 so that we avoid encoding errors.
    # Use codecs.open for Python 2 compatibility
    here = os.path.abspath(os.path.dirname(__file__))

    with codecs.open(os.path.join(here, *file_paths), 'r', 'latin1') as f:
        version_file = f.read()

    # The version line must have the form
    # __version__ = 'ver'
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

VERSION = find_version('trainbot', '__init__.py')


def get_install_requires():
    return []


setup(
    name='trainbot',
    packages=find_packages(),
    version=VERSION,
    description='Twitter & SMS bot to provide real time UK train timetables.',
    author='Paul M Furley',
    author_email='paul@paulfurley.com',
    # url='https://github.com/paulfurley/trainbot',
    # download_url=('https://github.com/paulfurley/encryptit/tarball/{0}'
    #               .format(VERSION)),
    install_requires=get_install_requires(),
    entry_points={
        'console_scripts': [
            'trainbot=trainbot.__main__:main',
        ],
    },
    test_suite='nose.collector',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'License :: Other/Proprietary License',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
