#!/bin/bash

sudo apt-get install python3-setuptools python3-dev build-essential virtualenv python-pytest

#sudo apt-key adv --keyserver hkp://pool.sks-keyservers.net --recv-keys 023EDB0B
#echo deb https://dl.bintray.com/gauge/gauge-deb stable main | sudo tee -a /etc/apt/sources.list
#sudo apt-get update && sudo apt-get install gauge

rm -rf venv3/
virtualenv -p python3 venv3
source venv3/bin/activate

pip install -r requirements/dev.txt
deactivate
