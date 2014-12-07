Summary:	Universal Addresses to RPC Program Number Mapper
Name:		rpcbind
Version:	0.2.1
Release:	8
License:	BSD
Group:		System/Servers
Url:		http://rpcbind.sourceforge.net/
Source0:	http://downloads.sourceforge.net/rpcbind/%{name}-%{version}.tar.bz2
Source1:	rpcbind.service
Source2:	rpcbind.sysconfig
Source3:	sbin.rpcbind.apparmor
Source4:	rpcbind.socket
Patch0:		rpcbind-0001-Remove-yellow-pages-support.patch
BuildRequires:	quota-devel
BuildRequires:	pkgconfig(libtirpc)
Requires(post,preun):	rpm-helper

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
#fix build with new automake
sed -i -e 's,AM_CONFIG_HEADER,AC_CONFIG_HEADERS,g' configure.*
autoreconf -fi

%build
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

