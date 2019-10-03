#!/bin/bash
set -e
set -u

######### sdopythonapp build site script #######
PWD="`pwd`"
PROG="`basename $0`"

MODE="$1"

INVENTORY="${PWD}/siteinventory.txt"

echo "sdopythonapp utility to run application using local dev_appserver.py"
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

if [ ! -d sdopythonapp/site ]
then
    echo "No 'sdopythonapp/site' directory - aborting"
    exit 1
fi

echo
echo "Run application from Local or Remote configuration files"
if [ "$MODE" = "DEPLOY"]
then
    echo "Local: deployed with pythonapp to gcloud"
else
    echo "Local: in this directory"
fi
echo "Remote: from remote URL eg. https://raw.githubusercontent.com/... "
while true
do
    read -r -p "Local or Remote? [L|R]: " response
    LR="$response"
    case $LR in
    l|L)
        REMOTE="N"
        break
        ;;
    r|R)
        REMOTE="Y"
        break
        ;;
    esac
done

if [ $REMOTE = "Y" ]
then
    TARGETURL=""
    while [ -z "$TARGETURL" ]
    do
        echo
        read -r -p "Root URL of configuration (eg. https://raw.githubusercontent.com/schemaorg/schemaorg/master): " response
        TESTURL="${response}/siteconfig.json"
        echo checking for siteconfig.json ...
        if curl -L --output /dev/null --silent --head --fail "$TESTURL"
        then
            echo "Success!"
            TARGETURL=$response
            break
        else
            echo "Cannot access $TESTURL"
        fi
    done
    
    if [ ! -f siteconfig.json ]
    then
        echo "No 'siteconfig.json' file - aborting"
        exit 1
    fi
    
#Empty site directory
    rm -rf sdopythonapp/site/*
    if [ -f handlers.yaml ]
    then
        cp handlers.yaml sdopythonapp/site
    fi
    
#Create siteconfig.json in site directory with redirect to remote config
    MATCH='"VOCABDEFLOC": ?".*"'
    SUB="\"VOCABDEFLOC\": \"${TARGETURL}\""
    TMP=".tmp.$$"
    echo -n "s@${MATCH}" > $TMP
    echo -n "@${SUB}" >> $TMP
    echo -n "@" >> $TMP
    sed -E -f $TMP siteconfig.json > sdopythonapp/site/siteconfig.json
    rm -f $TMP
    
fi

    
if [  -x ./runpythonpreprepare.sh ]
then
    echo "Running local preprepare script"
    ./runpythonpreprepare.sh $INVENTORY 
fi

if [  $REMOTE = "N" ]
then
    echo "Copying configuration"
    
    for i in `cat $INVENTORY`
    do 
        #rsync -r -u $i sdopythonapp/site 
        rsync -r -u $i sdopythonapp/site 
    done
fi

if [  -x ./runpythonpostprepare.sh ]
then
    echo "Running local postprepare script"
    ./runpythonpostprepare.sh $INVENTORY 
fi
