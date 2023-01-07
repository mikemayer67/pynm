from setuptools import find_packages
from setuptools import setup

import pynm

setup(
    name='pynm',
    version=pynm.version,
    packages=['pynm'],
    url='https://github.com/mikemayer67/pynm',
    license='unlicense',
    author='Michael Mayer',
    author_email='mikemayer67@vmwishes.com',
    description='Python Notification Manager',
    install_reqires=[],
)
