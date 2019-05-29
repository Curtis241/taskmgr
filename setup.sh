#!/bin/bash

rm -rf venv3/
virtualenv -p python3.6 venv3
source venv3/bin/activate
pip install -r requirements/dev.txt
deactivate
