#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['click==8.0.1', 'colored==1.4.2', 'beautifultable==1.0.1',
                'redis==4.4.4', 'redisearch==2.1.1', 'python-dateutil==2.8.2',
                'fastapi==0.75.1']
setup_requirements = ['pytest-runner', ]
test_requirements = ['pytest', ]

setup(
    author="Curtis Peterson",
    author_email='copeterson07@gmail.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.8',
        'Operating System :: POSIX :: Linux'

    ],
    description="Task Manager",
    entry_points='''
        [console_scripts]
        taskmgr=taskmgr.cli:cli
    ''',
    packages=['taskmgr', 'taskmgr.lib'],
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='taskmgr',
    name='taskmgr',
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/Curtis241/taskmgr',
    version='0.2.5',
    zip_safe=False,
)
