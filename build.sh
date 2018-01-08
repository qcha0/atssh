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

#####################################
cat > remove.sh <<EOF
#!/usr/bin/env bash

sed -ie '/export ATSSH_ROOT=.*/d' $1
sed -ie '/export PATH=\$ATSSH_ROOT\/bin:\$PATH/d' $1

rm -rf $ATSSH_ROOT
rm -f remove.sh
EOF
chmod +x remove.sh