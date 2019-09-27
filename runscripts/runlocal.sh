#!/bin/bash
set -e
set -u

######### sdopythonapp run local script #######
PWD="`pwd`"
PROG="`basename $0`"

echo "sdopythonapp utility to run application using local dev_appserver.py"
if [ ! -d sdopythonapp ]
then
    echo "No 'sdopythonapp' directory here aboorting!"
    exit 1
fi
if [ ! -d sdopythonapp/runscripts ]
then
    echo "No 'sdopythonapp/runscripts' directory here aboorting!"
    exit 1
fi
if [  -x ./runpreprepare.sh ]
then
    echo "Running local preprepare script"
    ./runpreprepare.sh
fi
if [  -x sdopythonapp/runscripts/runprepare.sh ]
then
    echo "Running master prepare script"
    ( cd sdopythonapp ; ./runscripts/runprepare.sh )
fi
if [  -x ./runpostprepare.sh ]
then
    echo "Running local postprepare script"
    ./runpostprepare.sh
fi

echo ${PROG}: Moving to 'sdopythonapp' directory
cd sdopythonapp

ARGS="--enable_host_checking false --clear_search_indexes yes app.yaml"
if [ ! -z "$*" ]
then
    ARGS=$@
fi

echo dev_appserver.py $ARGS
echo "(To override default dev_appserver.py arguments run '$PROG [ new arguments ]')"
echo

sleep 2
dev_appserver.py $ARGS