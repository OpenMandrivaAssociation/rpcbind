Summary:	Universal Addresses to RPC Program Number Napper
Name:		rpcbind
Version:	0.1.4
Release:	%mkrel 1
License:	GPL
Group:		System/Servers
URL:		http://nfsv4.bullopensource.org
Source0:	http://nfsv4.bullopensource.org/tarballs/rpcbind/rpcbind-0.1.4.tar.bz2
Source1:	rpcbind.init
Patch1:		rpcbind-0.1.4-compile.patch
Patch2:		rpcbind-0.1.4-debug.patch
Patch3:		rpcbind-0.1.4-warmstarts.patch
Patch4:		rpcbind-0.1.4-rpcuser.patch
BuildRequires:	libtool
BuildRequires:	libtirpc-devel >= 0.1.7
BuildRequires:	quota
Provides:	portmap = %{version}-%{release}
Obsoletes:	portmap <= 4.0-65.3
BuildRoot:	%{_tmppath}/%{name}-%{version}-root

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

%build
%ifarch s390 s390x
PIE="-fPIE"
%else
PIE="-fpie"
%endif
export PIE

RPCBUSR=rpc
RPCBDIR=%{_localstatedir}/%{name}
CFLAGS="`echo $RPM_OPT_FLAGS $ARCH_OPT_FLAGS $PIE`"

autoreconf -fisv

%configure2_5x \
    CFLAGS="$CFLAGS" LDFLAGS="-pie" \
    --enable-warmstarts \
    --with-statedir="$RPCBDIR" \
    --with-rpcuser="$RPCBUSR" \
    --enable-debug

%make all


%install
rm -rf %{buildroot}

install -d %{buildroot}%{_initrddir}
install -d %{buildroot}/sbin
install -d %{buildroot}%{_sbindir}
install -d %{buildroot}%{_localstatedir}/%{name}
install -d %{buildroot}%{_mandir}/man8

install -m0755 src/rpcbind %{buildroot}/sbin
install -m0755 src/rpcinfo %{buildroot}%{_sbindir}
install -m0755 %{SOURCE1} %{buildroot}%{_initrddir}/rpcbind
install -m0644 man/rpcbind.8 %{buildroot}%{_mandir}/man8
install -m0644 man/rpcinfo.8 %{buildroot}%{_mandir}/man8

%pre
# if the rpc uid and gid is left over from the portmapper
# remove both of them.
%{_sbindir}/userdel  rpc 2> /dev/null || :
%{_sbindir}/groupdel rpc 2> /dev/null || : 

# Now re-add the rpc uid/gid
%{_sbindir}/groupadd -g 32 rpc > /dev/null 2>&1
%{_sbindir}/useradd -l -c "Rpcbind Daemon" -d %{_localstatedir}/%{name} -g 32 \
    -M -s /sbin/nologin -u 32 rpc > /dev/null 2>&1

%post 
/sbin/chkconfig --add %{name}

%preun
if [ $1 -eq 0 ]; then
    service rpcbind stop > /dev/null 2>&1
    /sbin/chkconfig --del %{name}
	%{_sbindir}/userdel  rpc 2>/dev/null || :
	%{_sbindir}/groupdel rpc 2>/dev/null || :
	rm -rf /var/lib/rpcbind
fi
%postun
if [ "$1" -ge "1" ]; then
    service rpcbind condrestart > /dev/null 2>&1
fi

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc AUTHORS ChangeLog README
%{_initrddir}/rpcbind
/sbin/rpcbind
%{_sbindir}/rpcinfo
%{_mandir}/man8/*
%dir %attr(0700,rpc,rpc) %{_localstatedir}/%{name}
