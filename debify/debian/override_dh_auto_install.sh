#!/bin/bash

source debian/vars.sh

# TILL WE can work this out, we go with DNF
ls -ld *

cp universal-hooks-DNF.py universal-hooks.py
chmod a+x universal-hooks.py
mkdir -p apt/universal-hooks
