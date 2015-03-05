Name: yum-plugin-cpanel
Version: 0.1
Release: 1%{?dist}
Summary: Yum Plugin for cPanel servers

Group: Development/Tools
License: cPanel
Requires: yum-utils

%description
cPanel and 3rdparty developers can use this plugin to execute commands at various points in the yum process on cPanel servers.

%install
rm -rf %{buildroot}
install -m 644 %_sourcedir/cpanel.conf /etc/yum/pluginconf.d/cpanel.conf
install -m 755 %_sourcedir/cpanel.py /usr/lib/yum-plugins/cpanel.py
mkdir -p /etc/yum/cpanel

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
/usr/lib/yum-plugins/cpanel.py
%config(noreplace) /etc/yum/pluginconf.d/cpanel.conf
/etc/yum/cpanel/

%changelog
* Thu Mar 05 2015 Dan Muey <dan@cpanel.net> - 0.1-1
- implement spec file
