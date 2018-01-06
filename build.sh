#!/usr/bin/bash

ATSSH_ROOT=${HOME}/.atssh

if [ -z $1 ]; then
    echo "Please enter shell profile path"
    exit 1
fi

if [ ! -d ${ATSSH_ROOT} ]; then
    mkdir ${ATSSH_ROOT}/bin
fi

echo "export ATSSH_ROOT=${ATSSH_ROOT}"
echo "export PATH=\$ATSSH_ROOT/bin:\$PATH"

cp -f atssh ${ATSSH_ROOT}/bin
cp -f atssh.py ${ATSSH_ROOT}/bin
