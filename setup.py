#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['pip>=18.1', 'bumpversion>=0.5.3','wheel>=0.32.1','watchdog>=0.9.0',
                'click>=6.0', 'pyyaml>=3.12', 'colored>=1.3.93', 'beautifultable>=0.7.0',
                'requests>=2.22.0','google-auth==1.6.3', 'google-api-python-client==1.7.8',
                'google-auth-httplib2==0.0.3', 'google-auth-oauthlib==0.3.0',
                'google-cloud-datastore==1.9.0', 'protobuf==3.9.1', 'ujson==1.35', 'dpath==1.4.2', 'redis==3.3.11']
setup_requirements = ['pytest-runner', ]
test_requirements = ['pytest', ]

setup(
    author="Curtis Peterson",
    author_email='copeterson07@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Task Manager",
    entry_points='''
        [console_scripts]
        taskmgr=taskmgr.cli:cli
        gtask=taskmgr.gtask_cli:gtask_cli
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
    version='0.1.6',
    zip_safe=False,
)
