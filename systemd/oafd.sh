#!/bin/bash

HOME=/home/oaf
VENVDIR=$HOME/OpenAutomatedFarm/env34
CONFDIR=$HOME/OpenAutomatedFarm/FarmGUI

cd ${CONFDIR}
source ${VENVDIR}/bin/activate
oafd production.ini