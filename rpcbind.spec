Name:		rpcbind
Version:	0.2.1
Release:	3
Summary:	Universal Addresses to RPC Program Number Mapper
License:	BSD
Group:		System/Servers
URL:		http://rpcbind.sourceforge.net/
Source0:	http://downloads.sourceforge.net/rpcbind/%{name}-%{version}.tar.bz2
Source1: 	rpcbind.service
Source2:	rpcbind.sysconfig
Source3:	sbin.rpcbind.apparmor
Source4: 	rpcbind.socket

Patch0:		rpcbind-0001-Remove-yellow-pages-support.patch

BuildRequires:	tirpc-devel >= 0.1.7
BuildRequires:	quota
Obsoletes:	portmap
Conflicts:	apparmor-profiles < 2.1-1.961.4mdv2008.0
Requires(post):	rpm-helper
Requires(preun):rpm-helper

%description
The rpcbind utility is a server that converts RPC program numbers into
universal addresses.  It must be running on the host to be able to make RPC
calls on a server on that machine.

%prep
%setup -q
cp %{SOURCE1} .
cp %{SOURCE2} .
cp %{SOURCE4} .
%patch0 -p1 -b .noyp~

%build
#fix build with new automake
sed -i -e 's,AM_CONFIG_HEADER,AC_CONFIG_HEADERS,g' configure.*
autoreconf -fi
%serverbuild

%configure2_5x \
    CFLAGS="%{optflags} -fpie" LDFLAGS="-pie" \
    --enable-warmstarts \
    --with-statedir="%{_localstatedir}/lib/%{name}" \
    --with-rpcuser="rpc" \
    --enable-debug

%make all

%install
mkdir -p %{buildroot}%{_unitdir}
install -d %{buildroot}%{_localstatedir}/lib/%{name}
install -m755 rpcbind -D %{buildroot}/sbin/rpcbind
install -m755 rpcinfo -D %{buildroot}/sbin/rpcinfo
install -m644 %{SOURCE1} %{buildroot}%{_unitdir}
install -m644 %{SOURCE4} %{buildroot}%{_unitdir}
install -m644 rpcbind.sysconfig -D %{buildroot}%{_sysconfdir}/sysconfig/rpcbind
install -m644 man/rpcbind.8 -D %{buildroot}%{_mandir}/man8/rpcbind.8
install -m644 man/rpcinfo.8 -D %{buildroot}%{_mandir}/man8/rpcbind-rpcinfo.8

cat > README.urpmi << EOF

Because of file conflicts with glibc the following files has been renamed:

rpcinfo.8 -> rpcbind-rpcinfo.8

glibc also provides rpcinfo as /usr/sbin/rpcinfo, so the rpcinfo program
provided with this package is put in /sbin/rpcinfo
EOF

# apparmor profile
install -m644 %{SOURCE3} -D %{buildroot}%{_sysconfdir}/apparmor.d/sbin.rpcbind

%pre
%_pre_useradd rpc %{_localstatedir}/lib/%{name} /sbin/nologin

%post 
if [ $1 -gt 1 ] ; then 
#Need to clean up old init setup
    if [ -e /etc/init.d/rpcbind ]
    then
      /etc/init.d/rpcbind stop
      /bin/rm -f /etc/init.d/rpcbind
#Also add rpcbind as an alias in /etc/services
      sed -i''  '/sunrpc/s/\tportmapper/\trpcbind portmapper/g' /etc/services
else
# Initial installation
    /bin/systemctl enable rpcbind.service >/dev/null 
    /bin/systemctl start rpcbind.service
#And just in case add rpcbind as an alias in /etc/services
     sed -i''  '/sunrpc/s/\tportmapper/\trpcbind portmapper/g' /etc/services 2>&1 || :
    fi
fi
%_post_service %{name}
# restart running services depending on portmapper
for service in amd autofs bootparamd clusternfs mcserv \
		nfs-common nfs-server \
		ypserv ypbind yppasswdd ypxfrd; do
	if [ -f /var/lock/subsys/$service ]; then
		/sbin/service $service restart > /dev/null 2>/dev/null || :
	fi
done

%preun
%_preun_service %{name}

%posttrans
# if we have apparmor installed, reload if it's being used
if [ -x /sbin/apparmor_parser ]; then
	/sbin/service apparmor condreload
fi

%files
%doc AUTHORS COPYING ChangeLog README README.urpmi
%config(noreplace) %{_sysconfdir}/sysconfig/rpcbind
%config(noreplace) %{_sysconfdir}/apparmor.d/sbin.rpcbind
/sbin/rpcbind
/sbin/rpcinfo
%{_mandir}/man8/*
%dir %attr(0700,rpc,rpc) %{_localstatedir}/lib/%{name}
%{_unitdir}/rpcbind.service
%{_unitdir}/rpcbind.socket

%changelog
* Mon Feb 20 2012 abf
- The release updated by ABF

* Thu May 05 2011 Oden Eriksson <oeriksson@mandriva.com> 0.2.0-5mdv2011.0
+ Revision: 669433
- mass rebuild

* Fri Dec 03 2010 Oden Eriksson <oeriksson@mandriva.com> 0.2.0-4mdv2011.0
+ Revision: 607373
- rebuild

* Sun Mar 14 2010 Oden Eriksson <oeriksson@mandriva.com> 0.2.0-3mdv2010.1
+ Revision: 519067
- rebuild

* Sun Jun 07 2009 Guillaume Rousse <guillomovitch@mandriva.org> 0.2.0-2mdv2010.0
+ Revision: 383680
- rebuild with latest libtirpc

* Sun Jun 07 2009 Guillaume Rousse <guillomovitch@mandriva.org> 0.2.0-1mdv2010.0
+ Revision: 383524
- new version

* Tue May 05 2009 Guillaume Rousse <guillomovitch@mandriva.org> 0.1.7-2mdv2010.0
+ Revision: 372316
- rpcbind now replaces portmap

* Mon Jan 19 2009 Guillaume Rousse <guillomovitch@mandriva.org> 0.1.7-1mdv2009.1
+ Revision: 331276
- new version
- drop patches 1 and 2, merged upstream
- drop unapplied patch 3, seems to have been merged anyway

* Wed Dec 17 2008 Oden Eriksson <oeriksson@mandriva.com> 0.1.5-3mdv2009.1
+ Revision: 315260
- rebuild

* Fri Sep 05 2008 Guillaume Rousse <guillomovitch@mandriva.org> 0.1.5-2mdv2009.0
+ Revision: 281717
- don't try to source localization configuration file in service script, as there is no output to localize (bug #43227)

* Fri Jun 20 2008 Guillaume Rousse <guillomovitch@mandriva.org> 0.1.5-1mdv2009.0
+ Revision: 227546
- new version
- drop fedora patches, merged upstream
- disable temporarily apparmor patch, as it doesn't apply

* Wed Jun 18 2008 Thierry Vignaud <tv@mandriva.org> 0.1.4-11mdv2009.0
+ Revision: 225331
- rebuild

  + Pixel <pixel@mandriva.com>
    - adapt to %%_localstatedir now being /var instead of /var/lib (#22312)

* Thu Feb 28 2008 Guillaume Rousse <guillomovitch@mandriva.org> 0.1.4-10mdv2008.1
+ Revision: 176249
- fix crash when ipv6 is disabled

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Thu Nov 22 2007 Guillaume Rousse <guillomovitch@mandriva.org> 0.1.4-9mdv2008.1
+ Revision: 111196
- drop useless libtool build dependency
- file list cleanup
- don't remove data dir on uninstallation
- restart other services depending on portmapper after restarting itself

* Thu Sep 20 2007 Andreas Hasenack <andreas@mandriva.com> 0.1.4-8mdv2008.0
+ Revision: 91560
- add proper conflicts with apparmor-profiles (thanks soig)

* Wed Sep 19 2007 Andreas Hasenack <andreas@mandriva.com> 0.1.4-7mdv2008.0
+ Revision: 91065
- adjust (lib)tirpc-devel buildrequires
- fix warmstart (#31465, #31469)
- fix frequent user remove/add (#31467)
- add apparmor profile and use it if apparmor-parser
  is installed and running
- also drop to unprivileged group (and not just user)
- added some errno logging in the case of failures

* Fri Jun 22 2007 Andreas Hasenack <andreas@mandriva.com> 0.1.4-6mdv2008.0
+ Revision: 43185
- use %%serverbuild macro

* Tue May 15 2007 Guillaume Rousse <guillomovitch@mandriva.org> 0.1.4-5mdv2008.0
+ Revision: 26904
- don't obsolete portmap
  provides portmapper virtual package
  spec cleanup (we don't have s390 arch)

* Mon Apr 23 2007 Oden Eriksson <oeriksson@mandriva.com> 0.1.4-4mdv2008.0
+ Revision: 17344
- fix provides in lsb header (blino)

* Fri Apr 20 2007 Oden Eriksson <oeriksson@mandriva.com> 0.1.4-3mdv2008.0
+ Revision: 15359
- fix another file conflict

* Thu Apr 19 2007 Oden Eriksson <oeriksson@mandriva.com> 0.1.4-2mdv2008.0
+ Revision: 15028
- fix a file clash
- fix the initscript
- fix the %%post stuff

* Tue Apr 17 2007 Oden Eriksson <oeriksson@mandriva.com> 0.1.4-1mdv2008.0
+ Revision: 14046
- Import rpcbind



* Tue Apr 10 2007 Oden Eriksson <oeriksson@mandriva.com> 0.1.4-1mdv2007.1
- initial Mandriva package

* Fri Apr  6 2007 Steve Dickson <steved@redhat.com> 0.1.4-3
- Fixed the Provides and Obsoletes statments to correctly
  obsolete the portmap package.

* Tue Apr  3 2007 Steve Dickson <steved@redhat.com> 0.1.4-2
- Added dependency on glibc-common which allows the
  rpcinfo command to be installed in the correct place.
- Added dependency on man-pages so the rpcinfo man 
  pages don't conflict.
- Added the creation of /var/lib/rpcbind which will be
  used to store state files.
- Make rpcbind run with the 'rpc' uid/gid when it exists.

* Wed Feb 21 2007 Steve Dickson <steved@redhat.com> 0.1.4-1
- Initial commit
- Spec reviewed (bz 228894)
- Added the Provides/Obsoletes which should
  cause rpcbind to replace portmapper
