#!/bin/bash

I=1
while [ $I -lt 26 ]
do
    printf "%2.2s: " "$I"
    echo $I | bash runcpp.sh 2>&1 >$I.out
    N=`grep -E '^\[error |^\tat | cannot open library ' $I.out | wc -l`
    if [ 0 -lt "$N" ]
    then
        printf "FAIL\n"
    else
        printf "PASS\n"
    fi
    I=`expr $I + 1`
done
