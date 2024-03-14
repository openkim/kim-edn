"""Setuptools based setup module."""

from setuptools import setup, find_packages
import versioneer

setup(
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    zip_safe=True,
    packages=find_packages(exclude=("tests.*", "tests")),
    include_package_data=True,
)
