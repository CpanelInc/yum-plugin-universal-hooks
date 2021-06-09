#!/bin/bash

source debian/vars.sh

# We only support the DPkg:: version of these hook points, if that ever changes
#  this will need updated here and in apt-universal-hooks.pl
mkdir -p $DEB_INSTALL_ROOT/etc/apt/apt.conf.d
echo 'DPkg::Tools::Options::/etc/apt/universal-hooks/apt-universal-hooks.pl::Version "2";
DPkg::Pre-Invoke {"/etc/apt/universal-hooks/apt-universal-hooks.pl Pre-Invoke || true";}
DPkg::Pre-Install-Pkgs {"/etc/apt/universal-hooks/apt-universal-hooks.pl Pre-Install-Pkgs || true";};
DPkg::Post-Invoke {"/etc/apt/universal-hooks/apt-universal-hooks.pl Post-Invoke || true";}' > apt-universal-hooks.conf

mkdir -p $DEB_INSTALL_ROOT/etc/apt/universal-hooks
chmod 755 apt-universal-hooks.pl

