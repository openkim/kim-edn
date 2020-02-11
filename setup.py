"""Setuptools based setup module."""

from setuptools import setup, find_packages
import versioneer

SUMMARY = """
KIM-EDN encoder and decoder.
The KIM infrastructure embraces a subset of edn as a standard data format.
The primary purpose of this data format choice is to serve as a notational
superset to JSON with the enhancements being that it (1) allows for comments
and (2) treats commas as whitespace enabling easier templating.
`kim_edn` module exposes an API familiar to users of the standard library.
"""

setup(
    name='kim_edn',
    version=versioneer.get_version(),
    description='kim_edn - KIM-EDN encoder and decoder.',
    long_description=SUMMARY.strip(),
    url='https://github.com/yafshar/kim_edn',
    author='Yaser Afshar',
    author_email='yafshar@umn.edu',
    license='CDDL',
    classifiers=['Development Status :: 1 - Production/Stable',
                 'Intended Audience :: Science/Research',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 'Programming Language :: Python :: 3.7'],
    keywords='kim_edn',
    packages=find_packages(),
    install_requires=[],
    cmdclass=versioneer.get_cmdclass(),
)
