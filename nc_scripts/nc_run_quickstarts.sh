#!/bin/bash

if [ -z "$JAVA_HOME" ]
then
    JAVA_HOME=`/usr/libexec/java_home`
    echo "Setting JAVA_HOME to $JAVA_HOME"
fi
export JAVA_HOME

if ! echo $PATH | grep -E -e "^$JAVA_HOME/bin:|:$JAVA_HOME/bin\$|:$JAVA_HOME/bin:" >/dev/null 2>&1
then
    PATH=$PATH:$JAVA_HOME/bin
    echo "Adding $JAVA_HOME/bin to PATH"
fi

if [ -z "$GF_JAVA_HOME" ]
then
    GF_JAVA_HOME=$JAVA_HOME
    echo "Setting GF_JAVA_HOME to $GF_JAVA_HOME"
fi
export GF_JAVA_HOME

if [ -z "$GFCPP" ]
then
    GFCPP=/tmp/install
    echo "Setting GFCPP to $GFCPP"
fi
export GFCPP

if ! echo $LD_LIBRARY_PATH | grep -E -e "^$GFCPP/lib:|:$GFCPP/lib\$|:$GFCPP/lib:" >/dev/null 2>&1
then
    LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$GFCPP/lib
    echo "Adding $GFCPP/lib to LD_LIBRARY_PATH"
fi

if [ -z "$OPENSSL" ]
then
    OPENSSL=/opt/local
    echo "Setting OPENSSL to $OPENSSL"
fi
export OPENSSL

if ! echo $LD_LIBRARY_PATH | grep -E -e "^$OPENSSL/lib:|:$OPENSSL/lib\$|:$OPENSSL/lib:" >/dev/null 2>&1
then
    LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$OPENSSL/lib
    echo "Adding $OPENSSL/lib to LD_LIBRARY_PATH"
fi

if [ `uname` = "Darwin" ]
then
    DYLD_LIBRARY_PATH=$LD_LIBRARY_PATH
    export DYLD_LIBRARY_PATH
fi

run_quickstart() {
    printf "%2.2s: " "$1"
    echo $1 | bash runcpp.sh 2>&1 >$1.out
    N=`grep -E '^\[error |^\tat | cannot open library ' $1.out | wc -l`
    if [ 0 -lt "$N" ]
    then
        printf "FAIL\n"
    else
        printf "PASS\n"
    fi
}

if [ 0 -eq $# ]
then
    I=1
    while [ $I -lt 26 ]
    do
        run_quickstart $I
        I=`expr $I + 1`
    done
else
    while [ 0 -lt $# ]
    do
        run_quickstart $1
        shift
    done
fi
