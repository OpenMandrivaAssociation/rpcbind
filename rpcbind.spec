Name:		rpcbind
Version:	0.1.4
Release:	%mkrel 5
Summary:	Universal Addresses to RPC Program Number Napper
License:	GPL
Group:		System/Servers
URL:		http://nfsv4.bullopensource.org
Source0:	http://nfsv4.bullopensource.org/tarballs/rpcbind/rpcbind-0.1.4.tar.bz2
Source1:	rpcbind.init
Source2:	rpcbind.sysconfig
Patch1:		rpcbind-0.1.4-compile.patch
Patch2:		rpcbind-0.1.4-debug.patch
Patch3:		rpcbind-0.1.4-warmstarts.patch
Patch4:		rpcbind-0.1.4-rpcuser.patch
BuildRequires:	libtool
BuildRequires:	libtirpc-devel >= 0.1.7
BuildRequires:	quota
Provides:	    portmapper
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

cp %{SOURCE1} .
cp %{SOURCE2} .


%build
%configure2_5x \
    CFLAGS="%optflags -fpie" LDFLAGS="-pie" \
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

%pre
# if the rpc uid and gid is left over from the portmapper
# remove both of them.
%{_sbindir}/userdel  rpc 2> /dev/null || :
%{_sbindir}/groupdel rpc 2> /dev/null || : 

# Now re-add the rpc uid/gid
%_pre_useradd rpc %{_localstatedir}/%{name} /sbin/nologin

%post 
%_post_service %{name}

%preun
if [ $1 -eq 0 ]; then
    service %{name} stop > /dev/null 2>&1
%_preun_service %{name}
    %{_sbindir}/userdel  rpc 2>/dev/null || :
    %{_sbindir}/groupdel rpc 2>/dev/null || :
    rm -rf /var/lib/rpcbind
fi

%postun
if [ "$1" -ge "1" ]; then
    service %{name} condrestart > /dev/null 2>&1
fi
%_postun_userdel rpc

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc AUTHORS ChangeLog README README.urpmi
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/sysconfig/rpcbind
%attr(0755,root,root) %{_initrddir}/rpcbind
/sbin/rpcbind
/sbin/rpcinfo
%{_mandir}/man8/*
%dir %attr(0700,rpc,rpc) %{_localstatedir}/%{name}
