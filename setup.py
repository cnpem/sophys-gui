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
        'bluesky-widgets',
        'kafka-bluesky-live',
        'typesentry==0.2.7'
    ],
    include_package_data=True,
    packages=find_packages(),
    package_data={"": ["*.css", "*.yml", "*json"]},
    scripts=[
        'scripts/sophys-gui.py'
    ]
)
