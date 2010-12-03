Name:		rpcbind
Version:	0.2.0
Release:	%mkrel 4
Summary:	Universal Addresses to RPC Program Number Napper
License:	GPL
Group:		System/Servers
URL:		http://rpcbind.sourceforge.net/
Source0:	http://downloads.sourceforge.net/rpcbind/%{name}-%{version}.tar.bz2
Source1:	rpcbind.init
Source2:	rpcbind.sysconfig
Source3:    sbin.rpcbind.apparmor
BuildRequires:	tirpc-devel >= 0.1.7
BuildRequires:	quota
Obsoletes:	    portmap
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
cp %{SOURCE1} .
cp %{SOURCE2} .

%build
%serverbuild

%configure2_5x \
    CFLAGS="$RPM_OPT_FLAGS -fpie" LDFLAGS="-pie" \
    --enable-warmstarts \
    --with-statedir="%{_localstatedir}/lib/%{name}" \
    --with-rpcuser="rpc" \
    --enable-debug

%make all

%install
rm -rf %{buildroot}

install -d %{buildroot}%{_sysconfdir}/sysconfig
install -d %{buildroot}%{_initrddir}
install -d %{buildroot}/sbin
install -d %{buildroot}%{_localstatedir}/lib/%{name}
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
%_pre_useradd rpc %{_localstatedir}/lib/%{name} /sbin/nologin

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
%_preun_service %{name}

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
%{_initrddir}/rpcbind
%config(noreplace) %{_sysconfdir}/sysconfig/rpcbind
%config(noreplace) %{_sysconfdir}/apparmor.d/sbin.rpcbind
/sbin/rpcbind
/sbin/rpcinfo
%{_mandir}/man8/*
%dir %attr(0700,rpc,rpc) %{_localstatedir}/lib/%{name}
