#!/bin/sh

`dirname $0`/geode_run_tests.py \
    --integrated \
    --distributed \
    geode-protobuf-messages \
    geode-protobuf \
    geode-experimental-driver
