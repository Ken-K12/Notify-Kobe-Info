#!/bin/bash
filename=$1
cd "$(dirname $0)"

if [ -z "$1" ]; then
    echo "引数を指定してください"
    exit 1
fi

aws cloudformation validate-template \
--template-body file://$1