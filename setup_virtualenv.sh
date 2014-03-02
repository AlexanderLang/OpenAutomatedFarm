#!/bin/bash

# create the virtual environment
pyvenv-3.3 env33
# activate it
source env33/bin/activate
# install easy_install and pip
cd env33
curl -O http://python-distribute.org/distribute_setup.py
python3.3 distribute_setup.py
easy_install pip
# install pyramid
pip install pyramid
# install database libraries
cd ../../lib/plant_settings_database
python3.3 setup.py develop
cd ../field_controller_database
python3.3 setup.py develop
# install GUI
cd ../../FarmGUI
python3.3 setup.py develop

