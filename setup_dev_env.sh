#!/bin/bash


sudo apt-get install python3-setuptools python3-dev build-essential virtualenv

rm -rf venv3/
virtualenv -p python3 venv3
source venv3/bin/activate

pip install -r requirements/dev.txt
deactivate
