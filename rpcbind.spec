Name:		rpcbind
Version:	0.1.4
Release:	%mkrel 8
Summary:	Universal Addresses to RPC Program Number Napper
License:	GPL
Group:		System/Servers
URL:		http://nfsv4.bullopensource.org
Source0:	http://nfsv4.bullopensource.org/tarballs/rpcbind/rpcbind-0.1.4.tar.bz2
Source1:	rpcbind.init
Source2:	rpcbind.sysconfig
Source3:        sbin.rpcbind.apparmor
Patch1:		rpcbind-0.1.4-compile.patch
Patch2:		rpcbind-0.1.4-debug.patch
Patch3:		rpcbind-0.1.4-warmstarts.patch
Patch4:		rpcbind-0.1.4-rpcuser.patch
# http://qa.mandriva.com/show_bug.cgi?id=31465
Patch5:         rpcbind-0.1.4-warmstartperms.patch
# some better logging
Patch6:         rpcbind-0.1.4-errno.patch
# also switch to unprivileged group
Patch7:         rpcbind-0.1.4-setgid.patch
# move warm start read call to after we switched uid/gid, or
# else we need to add the dac_read_search and dac_override
# capabilities to the apparmor profile. These capabilities are
# basically what allow root to read files/dirs from other users
# which are mode 0600/0700 for example
Patch8:         rpcbind-0.1.4-movewarmstart.patch
BuildRequires:	libtool
BuildRequires:	tirpc-devel >= 0.1.7
BuildRequires:	quota
Provides:	portmapper
Conflicts:      apparmor-profiles < 2.1-1.961.4mdv2008.0
Requires(post): rpm-helper
Requires(preun): rpm-helper
BuildRoot:      %{_tmppath}/%{name}-%{version}

%description
The rpcbind utility is a server that converts RPC program numbers into
universal addresses.  It must be running on the host to be able to make RPC
calls on a server on that machine.

%prep
%setup -q

%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1 -b .orig
%patch6 -p1 -b .errno
%patch7 -p1 -b .setgid
%patch8 -p1 -b .movewarmstart

cp %{SOURCE1} .
cp %{SOURCE2} .


%build
%serverbuild

%configure2_5x \
    CFLAGS="$RPM_OPT_FLAGS -fpie" LDFLAGS="-pie" \
    --enable-warmstarts \
    --with-statedir="%{_localstatedir}/%{name}" \
    --with-rpcuser="rpc" \
    --enable-debug

%make all

%install
rm -rf %{buildroot}

install -d %{buildroot}%{_sysconfdir}/sysconfig
install -d %{buildroot}%{_initrddir}
install -d %{buildroot}/sbin
install -d %{buildroot}%{_localstatedir}/%{name}
install -d %{buildroot}%{_mandir}/man8

install -m0755 src/rpcbind %{buildroot}/sbin
install -m0755 src/rpcinfo %{buildroot}/sbin
install -m0755 rpcbind.init %{buildroot}%{_initrddir}/rpcbind
install -m0644 rpcbind.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/rpcbind
install -m0644 man/rpcbind.8 %{buildroot}%{_mandir}/man8/rpcbind.8
install -m0644 man/rpcinfo.8 %{buildroot}%{_mandir}/man8/rpcbind-rpcinfo.8

cat > README.urpmi << EOF

Because of file conflicts with glibc the following files has been renamed:

rpcinfo.8 -> rpcbind-rpcinfo.8

glibc also provides rpcinfo as /usr/sbin/rpcinfo, so the rpcinfo program
provided with this package is put in /sbin/rpcinfo
EOF

# apparmor profile
mkdir -p %{buildroot}%{_sysconfdir}/apparmor.d
install -m 0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/apparmor.d/sbin.rpcbind

%pre
%_pre_useradd rpc %{_localstatedir}/%{name} /sbin/nologin

%post 
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
if [ $1 -eq 0 ]; then
    service %{name} stop > /dev/null 2>&1
%_preun_service %{name}
    rm -rf /var/lib/rpcbind
fi

%posttrans
# if we have apparmor installed, reload if it's being used
if [ -x /sbin/apparmor_parser ]; then
        /sbin/service apparmor condreload
fi

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc AUTHORS ChangeLog README README.urpmi
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/sysconfig/rpcbind
%attr(0755,root,root) %{_initrddir}/rpcbind
%config(noreplace) %{_sysconfdir}/apparmor.d/sbin.rpcbind
/sbin/rpcbind
/sbin/rpcinfo
%{_mandir}/man8/*
%dir %attr(0700,rpc,rpc) %{_localstatedir}/%{name}
