Summary:	Universal Addresses to RPC Program Number Mapper
Name:		rpcbind
Version:	1.2.5
Release:	1
License:	BSD
Group:		System/Servers
Url:		http://rpcbind.sourceforge.net/
Source0:	http://downloads.sourceforge.net/rpcbind/%{name}-%{version}.tar.bz2
Source1:	rpcbind.sysconfig
Source2:	sbin.rpcbind.apparmor

Patch0:		rpcbind-1.2.5-rpcinfo-bufoverflow.patch
Patch1:		rpcbind-0.2.3-systemd-envfile.patch
Patch2:		rpcbind-0.2.3-systemd-tmpfiles.patch
Patch3:		rpcbind-0.2.4-runstatdir.patch
Patch4:		rpcbind-0.2.4-systemd-service.patch
Patch5:		rpcbind-0.2.4-systemd-rundir.patch
BuildRequires:	quota-devel
BuildRequires:	pkgconfig(libtirpc)
BuildRequires:	pkgconfig(libsystemd)
BuildRequires:	systemd-macros
BuildRequires:	rpm-helper
Requires(pre):	rpm-helper

%description
The rpcbind utility is a server that converts RPC program numbers into
universal addresses.  It must be running on the host to be able to make RPC
calls on a server on that machine.

%prep
%autosetup -p1
cp -f %{SOURCE1} .

%build
%serverbuild
%configure \
	CFLAGS="%{optflags} -fpie" LDFLAGS="-pie" \
	--enable-warmstarts \
	--with-statedir="%{_rundir}/rpcbind" \
	--with-rpcuser="rpc" \
	--with-systemdsystemunitdir=%{_unitdir} \
	--sbindir=/sbin

%make_build all

%install
mkdir -p %{buildroot}{/sbin,%{_bindir},%{_sysconfdir}/sysconfig}
mkdir -p %{buildroot}%{_unitdir}
mkdir -p %{buildroot}%{_tmpfilesdir}
mkdir -p %{buildroot}%{_mandir}/man8
mkdir -p %{buildroot}%{rpcbind_state_dir}
%make_install

install -m644 %{SOURCE1} -D %{buildroot}%{_sysconfdir}/sysconfig/rpcbind

# apparmor profile
install -m644 %{SOURCE2} -D %{buildroot}%{_sysconfdir}/apparmor.d/sbin.rpcbind

install -d %{buildroot}%{_presetdir}
cat > %{buildroot}%{_presetdir}/86-%{name}.preset << EOF
enable rpcbind.socket
EOF

%pre
%_pre_useradd rpc %{_localstatedir}/lib/%{name} /sbin/nologin

%posttrans
# if we have apparmor installed, reload if it's being used
if [ -x /sbin/apparmor_parser ]; then
    /sbin/service apparmor condreload
fi

%files
%doc AUTHORS COPYING ChangeLog
%config(noreplace) %{_sysconfdir}/sysconfig/rpcbind
%config(noreplace) %{_sysconfdir}/apparmor.d/sbin.rpcbind
/sbin/rpcbind
/sbin/rpcinfo
%{_tmpfilesdir}/rpcbind.conf
%{_mandir}/man8/*
%dir %attr(0700,rpc,rpc) %{_localstatedir}/lib/%{name}
%{_unitdir}/rpcbind.service
%{_unitdir}/rpcbind.socket
%{_presetdir}/86-%{name}.preset
