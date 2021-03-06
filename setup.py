#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['pip==19.3.1', 'bumpversion>=0.5.3','wheel==0.32.1','watchdog==0.9.0',
                'click==7.0', 'colored==1.4.2', 'pyyaml==3.12', 'ujson==1.35',  'beautifultable==1.0.0',
                'requests==2.22.0','dpath==1.4.2','redis==3.3.11', 'google-auth>=1.21.1', 'google-api-python-client>=1.7.8',
                'google-auth-httplib2>=0.0.3', 'google-auth-oauthlib>=0.3.0', 'google-cloud-datastore>=1.9.0']
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
        'Programming Language :: Python :: 3.8',

    ],
    description="Task Manager",
    entry_points='''
        [console_scripts]
        taskmgr=taskmgr.cli:cli
        gtask=taskmgr.gtask_cli:gtask_cli
        taskmgrapi=taskmgr.api
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
    version='0.2.0',
    zip_safe=False,
)
