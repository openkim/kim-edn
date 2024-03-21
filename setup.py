"""Setuptools based setup module."""

from setuptools import setup

import versioneer


setup(
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
)
