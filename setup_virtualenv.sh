#!/bin/bash

# define some variables
ENV_DIR="env34"

# display greeting message
printf "***OAF*** Setup OpenAutomatedFarm virtual python environment:"

# create the virtual environment
printf "***OAF*** create virtual environment..."
pyvenv-3.4 $ENV_DIR
if [ $? -ne 0 ] ; then
	printf "failed\n"
	exit 1
fi
printf "***OAF*** done (create virtualenv)\n"

# activate it
printf "***OAF*** activate virtual environment..."
source $ENV_DIR/bin/activate
if [ $? -ne 0 ] ; then
	printf "failed (activate virtualenv)\n"
	exit 1
fi
printf "***OAF*** done(activate virtualenv)\n"

#cd $ENV_DIR
# ubuntu does not install pip, so...
# install easy_install and pip
#printf "***OAF*** install pip..."
#curl -O http://python-distribute.org/distribute_setup.py
#if [ $? -ne 0 ] ; then
#	printf "***OAF*** failed (download)\n"
#	exit 1
#fi
#python3.4 distribute_setup.py
#if [ $? -ne 0 ] ; then
#	printf "***OAF*** failed (distribute_setup.py)\n"
#	exit 1
#fi
#easy_install-3.4 pip
#if [ $? -ne 0 ] ; then
#	printf "***OAF*** failed (easy_install pip)\n"
#	exit 1
#fi
#printf "***OAF*** done (install pip)\n"

# install farmGui (pyramid app)
printf "  installing FarmGUI (pyramid app)..."
cd FarmGUI
python3.4 setup.py develop
if [ $? -ne 0 ] ; then
	printf "failed\n"
	exit 1
fi
printf "done\n"

echo -e "\n\n\n"
echo -e "OpenAutomatedFarm environment setup successful!!!"
echo -e "\n\n"


