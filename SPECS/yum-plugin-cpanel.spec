Name: yum-plugin-cpanel
Version: 0.1
Release: 2%{?dist}
Summary: Yum Plugin for cPanel servers

Group: Development/Tools
License: cPanel
Requires: yum-utils

%description
cPanel and 3rdparty developers can use this plugin to execute commands at various points in the yum process on cPanel servers.

%install
rm -rf %{buildroot}
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/yum/pluginconf.d
mkdir -p $RPM_BUILD_ROOT%{_libdir}/yum-plugins
install -m 644 %_sourcedir/cpanel.conf $RPM_BUILD_ROOT%{_sysconfdir}/yum/pluginconf.d/cpanel.conf
install -m 755 %_sourcedir/cpanel.py $RPM_BUILD_ROOT%{_libdir}/yum-plugins/cpanel.py
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/yum/cpanel

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{_libdir}/yum-plugins/cpanel.py*
%config(noreplace) %{_sysconfdir}/yum/pluginconf.d/cpanel.conf
%{_sysconfdir}/yum/cpanel

%changelog
* Thu Mar 05 2015 Dan Muey <dan@cpanel.net> - 0.1-1
- implement spec file
