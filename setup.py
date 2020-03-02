"""Setuptools based setup module."""

from setuptools import setup, find_packages
import versioneer

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='kim-edn',
    version=versioneer.get_version(),
    description='kim-edn - KIM-EDN encoder and decoder.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/openkim/kim-edn',
    author='Yaser Afshar',
    author_email='yafshar@umn.edu',
    license='CDDL-1.0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: Common Development and Distribution License 1.0 (CDDL-1.0)',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
    python_requires='>=3.6',
    keywords=['kim-edn', 'edn'],
    packages=find_packages(),
    install_requires=[],
    cmdclass=versioneer.get_cmdclass(),
)
