#!/bin/bash
set -e
set -u

######### sdopythonapp run app deploy script #######
PWD="`pwd`"
PROG="`basename $0`"
export PARENTDIR=$PWD

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
if [ ! -x sdopythonapp/runscripts/buildsite.sh ]
then
    echo "No 'sdopythonapp/runscripts/buildsite.sh' here aborting!"
    exit 1
fi

sdopythonapp/runscripts/buildsite.sh DEPLOY

echo ${PROG}: Moving to 'sdopythonapp' directory
cd sdopythonapp

deploy/deploy2gcloud.sh

#scripts/appdeploy.sh $@