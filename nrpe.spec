%define nsport 5666

Name: nrpe
Version: 2.12
Release: 8%{?dist}
Summary: Host/service/network monitoring agent for Nagios

Group: Applications/System
License: GPLv2
URL: http://www.nagios.org
Source0: http://dl.sourceforge.net/nagios/%{name}-%{version}.tar.gz
Source1: nrpe.sysconfig
Patch0: nrpe-initreload.patch
Patch1:	nrpe-read-extra-conf.patch

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires: openssl-devel tcp_wrappers

Requires(pre): %{_sbindir}/useradd
Requires(preun): /sbin/service, /sbin/chkconfig
Requires(post): /sbin/chkconfig, /sbin/service
Requires(postun): /sbin/service
Provides: nagios-nrpe = %{version}-%{release}

%description
Nrpe is a system daemon that will execute various Nagios plugins
locally on behalf of a remote (monitoring) host that uses the
check_nrpe plugin.  Various plugins that can be executed by the 
daemon are available at:
http://sourceforge.net/projects/nagiosplug

This package provides the core agent.

%package -n nagios-plugins-nrpe
Group: Applications/System
Summary: Provides nrpe plugin for Nagios
Requires: nagios-plugins
Provides: check_nrpe = %{version}-%{release}

%description -n nagios-plugins-nrpe
Nrpe is a system daemon that will execute various Nagios plugins
locally on behalf of a remote (monitoring) host that uses the
check_nrpe plugin.  Various plugins that can be executed by the 
daemon are available at:
http://sourceforge.net/projects/nagiosplug

This package provides the nrpe plugin for Nagios-related applications.

%prep
%setup -q
%patch0 -p0
%patch1 -p0 -b .sysconfig

%build
CFLAGS="$RPM_OPT_FLAGS" CXXFLAGS="$RPM_OPT_FLAGS" \
./configure \
	--with-init-dir=%{_initrddir} \
	--with-nrpe-port=%{nsport} \
	--with-nrpe-user=nrpe \
	--with-nrpe-group=nrpe \
	--bindir=%{_sbindir} \
	--libdir=/doesnt/matter/ \
	--libexecdir=%{_libdir}/nagios/plugins \
	--datadir=%{_datadir}/nagios \
	--sysconfdir=%{_sysconfdir}/nagios \
	--localstatedir=%{_localstatedir}/log/nagios \
	--enable-command-args
make %{?_smp_mflags} all
sed -i "s/# chkconfig: 2345/# chkconfig: - /" init-script

%install
rm -rf %{buildroot}
install -D -p -m 0755 init-script %{buildroot}/%{_initrddir}/nrpe
install -D -p -m 0644 sample-config/nrpe.cfg %{buildroot}/%{_sysconfdir}/nagios/nrpe.cfg
install -D -p -m 0755 src/nrpe %{buildroot}/%{_sbindir}/nrpe
install -D -p -m 0755 src/check_nrpe %{buildroot}/%{_libdir}/nagios/plugins/check_nrpe
install -D -p -m 0644 %{SOURCE1} %{buildroot}/%{_sysconfdir}/sysconfig/%{name}

%clean
rm -rf %{buildroot}

%pre
%{_sbindir}/useradd -c "NRPE user for the NRPE service" -d / -r -s /sbin/nologin nrpe 2> /dev/null || :

%preun
if [ $1 = 0 ]; then
	/sbin/service %{name} stop > /dev/null 2>&1 || :
	/sbin/chkconfig --del %{name} || :
fi

%post
/sbin/chkconfig --add %{name} || :

%postun
if [ "$1" -ge "1" ]; then
	/sbin/service %{name} condrestart > /dev/null 2>&1 || :
fi

%files
%defattr(-,root,root,-)
%{_initrddir}/nrpe
%{_sbindir}/nrpe
%dir %{_sysconfdir}/nagios
%config(noreplace) %{_sysconfdir}/nagios/nrpe.cfg
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%doc Changelog LEGAL README README.SSL SECURITY docs/NRPE.pdf

%files -n nagios-plugins-nrpe
%defattr(-,root,root,-)
%{_libdir}/nagios/*
%doc Changelog LEGAL README

%changelog
* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.12-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sun Feb 21 2009 Mike McGrath <mmcgrath@redhat.com> - 2.12-7
- Re-fix for 477527

* Mon Feb  2 2009 Peter Lemenkov <lemenkov@gmail.com> - 2.12-6
- Fixed BZ# 449174
- Clean up (in order to disable rpmlint warnings)

* Sat Jan 17 2009 Tomas Mraz <tmraz@redhat.com> - 2.12-5
- rebuild with new openssl

* Sun Dec 21 2008 Mike McGrath <mmcgrath@redhat.com> - 2.12-4
- Added some doc lines for ticket 477527

* Fri Dec 19 2008 Mike McGrath <mmcgrath@redhat.com> - 2.12-3
- Added Provides: nagios-nrpe

* Fri Dec 19 2008 Mike McGrath <mmcgrath@redhat.com> - 2.12-2
- Upstreamreleased new version

* Tue Feb 12 2008 Mike McGrath <mmcgrath@redhat.com> - 2.7-6
- Rebuild for gcc43

* Wed Dec 05 2007 Release Engineering <rel-eng at fedoraproject dot org> - 2.7-5
 - Rebuild for deps

* Wed Aug 22 2007 Mike McGrath <mmcgrath@redhat.com> 2.7-4
- License Change
- Rebuild for BuildID

* Fri Feb 23 2007 Mike McGrath <mmcgrath@redhat.com> 2.7-1
- Upstream released new version

* Sun Jul 23 2006 Mike McGrath <imlinux@gmail.com> 2.5.2-3
- no longer owns libdir/nagios
- buildrequires tcp_wrappers

* Sun Jul 23 2006 Mike McGrath <imlinux@gmail.com> 2.5.2-2
- Specify bogus libdir so rpmlint won't complain

* Mon Jul 03 2006 Mike McGrath <imlinux@gmail.com> 2.5.2-1
- Upstream released new version

* Mon Mar 12 2006 Mike McGrath <imlinux@gmail.com> 2.4-3
- Added description to useradd statement

* Sun Mar 05 2006 Mike McGrath <imlinux@gmail.com> 2.4-2
- Added proper SMP build flags
- Added %{?dist} tag
- Added reload to nrpe script
- Updated to 2.4, changes include: 
- Added option to allow week random seed (Gerhard Lausser)
- Added optional command line prefix (Sean Finney)
- Added ability to reload config file with SIGHUP
- Fixed bug with location of dh.h include file
- Fixed bug with disconnect message in debug mode

* Sat Feb 04 2006 Mike McGrath <imlinux@gmail.com> 2.3-1
- Created a Fedora friendly spec file

* Mon Jan 23 2006 Andreas Kasenides ank<@>cs.ucy.ac.cy
- fixed nrpe.cfg relocation to sample-config
- replaced Copyright label with License
- added --enable-command-args to enable remote arg passing (if desired can be disabled by commenting out)

* Wed Nov 12 2003 Ingimar Robertsson <iar@skyrr.is>
- Added adding of nagios group if it does not exist.

* Tue Jan 07 2003 James 'Showkilr' Peterson <showkilr@showkilr.com>
- Removed the lines which removed the nagios user and group from the system
- changed the patch release version from 3 to 1

* Mon Jan 06 2003 James 'Showkilr' Peterson <showkilr@showkilr.com>
- Removed patch files required for nrpe 1.5
- Update spec file for version 1.6 (1.6-1)

* Sat Dec 28 2002 James 'Showkilr' Peterson <showkilr@showkilr.com>
- First RPM build (1.5-1)
