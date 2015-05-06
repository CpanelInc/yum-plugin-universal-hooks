Name: yum-plugin-cpanel
Version: 0.1
Release: 5%{?dist}
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
install -m 644 %_sourcedir/universal-hooks.conf $RPM_BUILD_ROOT%{_sysconfdir}/yum/pluginconf.d/universal-hooks.conf
install -m 755 %_sourcedir/universal-hooks.py $RPM_BUILD_ROOT%{yum_pluginslib}/universal-hooks.py
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/yum/universal-hooks

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{yum_pluginslib}/universal-hooks.py*
%config(noreplace) %{_sysconfdir}/yum/pluginconf.d/universal-hooks.conf
%{_sysconfdir}/yum/universal-hooks

%changelog
* Wed May 06 2015 Dan Muey <dan@cpanel.net> - 0.1-5
- Rename to a more descriptive, non-cpanel specific name (since it can be used on any server)

* Wed May 06 2015 Dan Muey <dan@cpanel.net> - 0.1-4
- Update license from cpanel to BSD 2-Clause

* Tue Mar 10 2015 Dan Muey <dan@cpanel.net> - 0.1-3
- use yum_pluginslib instead of _libdir for the plugins path

* Thu Mar 06 2015 Dan Muey <dan@cpanel.net> - 0.1-2
- path fixes

* Thu Mar 05 2015 Dan Muey <dan@cpanel.net> - 0.1-1
- implement spec file
