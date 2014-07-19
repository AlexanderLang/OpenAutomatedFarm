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

cd $ENV_DIR
# ubuntu does not install pip, so...
# install easy_install and pip
printf "***OAF*** install pip..."
curl -O http://python-distribute.org/distribute_setup.py
if [ $? -ne 0 ] ; then
	printf "***OAF*** failed (download)\n"
	exit 1
fi
python3.4 distribute_setup.py
if [ $? -ne 0 ] ; then
	printf "***OAF*** failed (distribute_setup.py)\n"
	exit 1
fi
easy_install-3.4 pip
if [ $? -ne 0 ] ; then
	printf "***OAF*** failed (easy_install pip)\n"
	exit 1
fi
printf "***OAF*** done (install pip)\n"

# install pyramid
printf "***OAF*** install pyramid..."
pip install pyramid
if [ $? -ne 0 ] ; then
	printf "***OAF*** failed (install pyramid)\n"
	exit 1
fi
printf "***OAF*** done (install pyramid)\n"

# install redis
printf "***OAF*** install redis..."
pip install redis
if [ $? -ne 0 ] ; then
	printf "***OAF*** failed (rq-scheduler)\n"
	exit 1
fi
printf "***OAF*** done (redis)\n"
# install hiredis to speed up redis-py
printf "***OAF*** install hiredis (for redis-py)..."
pip install hiredis
if [ $? -ne 0 ] ; then
	printf "***OAF*** failed (hiredis)\n"
	exit 1
fi

# install gevent-socketio
#printf "  install gevent-socketio..."
#pip install cython git+git://github.com/surfly/gevent.git#egg=gevent >>$LOG_FILE 2>&1
#if [ $? -ne 0 ] ; then
	#	printf "failed (cpython)\n"
	#exit 1
#fi
#pip install git+git://github.com/surfly/gevent.git#egg=gevent >>$LOG_FILE 2>&1
#if [ $? -ne 0 ] ; then
	#	printf "failed (gevent)\n"
	#	exit 1
#fi
#pip install gevent-socketio >>$LOG_FILE 2>&1
#if [ $? -ne 0 ] ; then
	#	printf "failed\n"
	#	exit 1
#fi
#printf "done\n"
# for speeding up gevent-websocket:
#printf "  install wsaccel and ujson (for websocket speedup)..."
#pip install wsaccel  >>$LOG_FILE 2>&1
#if [ $? -ne 0 ] ; then
	#	printf "failed\n"
	#	exit 1
#fi
#pip install ujson  >>$LOG_FILE 2>&1
#if [ $? -ne 0 ] ; then
	#	printf "failed\n"
	#	exit 1
#fi
#printf "done\n"

# install database libraries
printf "  install development libraries..."
cd ../lib/plant_settings_database
python3.4 setup.py develop
if [ $? -ne 0 ] ; then
	printf "failed (plant_settings)\n"
	exit 1
fi
cd ../field_controller_database
python3.4 setup.py develop
if [ $? -ne 0 ] ; then
	printf "failed (field_controller)\n"
	exit 1
fi
cd ../periphery_controller_communication
python3.4 setup.py develop
if [ $? -ne 0 ] ; then
	printf "failed (periphery_controller_communication)\n"
	exit 1
fi
printf "done\n"

# install farmGui (pyramid app)
printf "  installing FarmGUI (pyramid app)..."
cd ../../FarmGUI
python3.4 setup.py develop
if [ $? -ne 0 ] ; then
	printf "failed\n"
	exit 1
fi
printf "done\n"

echo -e "\n\n\n"
echo -e "OpenAutomatedFarm environment setup successful!!!"
echo -e "\n\n"


