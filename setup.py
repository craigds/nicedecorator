#!/usr/bin/env python
from distutils.core import setup
from os.path import abspath, dirname, join


def read_relative_file(filename):
    """Returns contents of the given file, whose path is supposed relative
    to this module."""
    with open(join(dirname(abspath(__file__)), filename)) as f:
        return f.read()


setup(
    name='nicedecorator',
    description='''A *nice* way of doing decorators in Python.''',
    version=read_relative_file('VERSION').strip(),
    author='Craig de Stigter',
    author_email='craig.ds@gmail.com',
    url='http://github.com/craigds/nicedecorator',
    py_modules=['nicedecorator'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: 3.3',
        'Topic :: Utilities'
    ],
)
