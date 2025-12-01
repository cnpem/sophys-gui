#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='sophys-gui',
    version='0.16.1',
    author='SWC - LNLS',
    description='Control GUI for the Bluesky queue.',
    install_requires=[
        'QtPy==2.3.1',
        'QtAwesome>1.2.3',
        'bluesky-queueserver-api==0.0.10',
        'bluesky-widgets',
        'typesentry==0.2.7',
        'numpy>=2.0.0',
        'assonant[naming-standards]',
        'sophys_live_view',
        'PyYAML',
    ],
    include_package_data=True,
    packages=find_packages(),
    package_data={"": ["*.css", "*.yml", "*json"]},
    entry_points={
        'gui_scripts': [
            'sophys-gui = sophys_gui.__main__:main',
        ]
    }
)
