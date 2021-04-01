#!/bin/bash

source debian/vars.sh

echo "TO BE DONE in case ZC-8252" > README.txt
echo "PWD" `pwd`
ls -ld *
mkdir -p $DEB_INSTALL_ROOT/etc/apt/universal-hooks

