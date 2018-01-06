#!/usr/bin/env bash

ATSSH_ROOT=$HOME/.atssh

if [ -z $1 ]; then
    echo "Please enter shell profile path"
    echo "Just like ~/.zshrc ~/.bashrc"
    exit 1
fi

if [ ! -d $ATSSH_ROOT ]; then
    mkdir -p $ATSSH_ROOT/bin
fi

echo "export ATSSH_ROOT=$ATSSH_ROOT" >> $1
echo "export PATH=\$ATSSH_ROOT/bin:\$PATH" >> $1
export ATSSH_ROOT=$ATSSH_ROOT
export PATH=$ATSSH_ROOT/bin:$PATH

cp -f atssh $ATSSH_ROOT/bin
cp -f atssh.py $ATSSH_ROOT/bin
chmod +x $ATSSH_ROOT/bin/atssh
