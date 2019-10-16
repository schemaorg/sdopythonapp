#!/bin/bash
set -e
set -u

######### sdopythonapp run local script #######
PWD="`pwd`"
PROG="`basename $0`"

echo "sdopythonapp utility to run application using local dev_appserver.py"

if [ ! -d sdopythonapp ]
then
    echo "No 'sdopythonapp' directory here aborting!"
    exit 1
fi

if [ ! -d sdopythonapp/runscripts ]
then
    echo "No 'sdopythonapp/runscripts' directory here aborting!"
    exit 1
fi

if [ ! -x sdopythonapp/runscripts/buildsite.sh ]
then
    echo "No 'sdopythonapp/runscripts/buildsite.sh' here aborting!"
    exit 1
fi

sdopythonapp/runscripts/buildsite.sh LOCAL

if [ -f app.yaml ]
then 
    echo "Copying app.yaml to local.yaml for running"
    cp app.yaml sdopythonapp/local.yaml
fi

echo ${PROG}: Moving to 'sdopythonapp' directory
cd sdopythonapp

if [ ! -f local.yaml ]
then
    echo "No local - copying default app.yaml to local.yaml for running"
    cp app.yaml local.yaml
fi

ARGS="--enable_host_checking false --clear_search_indexes yes local.yaml"
if [ ! -z "$*" ]
then
    ARGS=$@
fi

echo dev_appserver.py $ARGS
echo "(To override default dev_appserver.py arguments run '$PROG [ new arguments ]')"
echo

sleep 2
dev_appserver.py $ARGS