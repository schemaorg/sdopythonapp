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

function usage {
    echo "usage: $(basename $0) -e -m [-p project] [-v version] [-y yaml file]"
	echo "-e bypasses exercise of site step"
	echo "-m bypasses migrate traffic to new version step"
}

PROJECT=""
VERSION=""
YAML=""
CONF=""
EXE="Y"
MIG="Y"
while getopts 'p:v:y:em' OPTION; do
  case "$OPTION" in
    e)
      EXE="N"
    ;;
    m)
        MIG="N"
    ;;
    y)
        YAML="$OPTARG"
    ;;

    p)
        PROJECT="$OPTARG"
    ;;

    v)
        VERSION="$OPTARG"
    ;;


    ?)
        usage
        exit 1
    ;;
  esac
done


sdopythonapp/runscripts/buildsite.sh DEPLOY

echo ${PROG}: Moving to 'sdopythonapp' directory
cd sdopythonapp

runscripts/deploy2gcloud.sh $@

