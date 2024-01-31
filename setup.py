#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='sophys-gui',
    version='0.1.0',
    author='lnls-sirius',
    description='Control GUI for the Bluesky queue.',
    install_requires=[
        'QtPy==2.3.1',
        'QtAwesome==1.2.3',
        'bluesky-queueserver-api==0.0.10',
        'bluesky-widgets==0.0.15'
    ],
    include_package_data=True,
    packages=find_packages(),
    package_data={"": ["*.svg", "*.css", "*.yml"]},
    scripts=[
        'scripts/sophys-gui.py'
    ]
)
