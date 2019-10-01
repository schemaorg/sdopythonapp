#!/bin/bash
set -e
set -u

######### sdopythonapp run local script #######
PWD="`pwd`"
PROG="`basename $0`"
INVENTORY="${PWD}/siteinventory.txt"
PARENTDIR=${PWD} ; export PARENTDIR
echo "sdopythonapp utility to deploy application gcloud app deploy"
if [ ! -f $INVENTORY ]
then
    echo "No 'siteinventory.txt' file here aboorting!"
    exit 1
fi
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
    
if [  -x ./runpythonpreprepare.sh ]
then
    echo "Running local preprepare script"
    ./runpythonpreprepare.sh $INVENTORY 
fi
if [  -x sdopythonapp/runscripts/runpythonprepare.sh ]
then
    echo "Running master prepare script"
    ( cd sdopythonapp ; ./runscripts/runpythonprepare.sh $INVENTORY )
fi
if [  -x ./runpythonpostprepare.sh ]
then
    echo "Running local postprepare script"
    ./runpythonpostprepare.sh $INVENTORY 
fi

echo ${PROG}: Moving to 'sdopythonapp' directory
cd sdopythonapp

deploy/deploy2gcloud.sh

#scripts/appdeploy.sh $@