Name: yum-plugin-cpanel
Version: 0.1
Release: 3%{?dist}
Summary: Yum Plugin for cPanel servers

Group: Development/Tools
License: cPanel
Requires: yum-utils

%define yum_pluginslib  /usr/lib/yum-plugins

%description
cPanel and 3rdparty developers can use this plugin to execute commands at various points in the yum process on cPanel servers.

%install
rm -rf %{buildroot}
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/yum/pluginconf.d
mkdir -p $RPM_BUILD_ROOT%{yum_pluginslib}
install -m 644 %_sourcedir/cpanel.conf $RPM_BUILD_ROOT%{_sysconfdir}/yum/pluginconf.d/cpanel.conf
install -m 755 %_sourcedir/cpanel.py $RPM_BUILD_ROOT%{yum_pluginslib}/cpanel.py
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/yum/cpanel

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{yum_pluginslib}/cpanel.py*
%config(noreplace) %{_sysconfdir}/yum/pluginconf.d/cpanel.conf
%{_sysconfdir}/yum/cpanel

%changelog
* Tue Mar 10 2015 Dan Muey <dan@cpanel.net> - 0.1-3
- use yum_pluginslib instead of _libdir for the plugins path

* Thu Mar 06 2015 Dan Muey <dan@cpanel.net> - 0.1-2
- path fixes

* Thu Mar 05 2015 Dan Muey <dan@cpanel.net> - 0.1-1
- implement spec file
