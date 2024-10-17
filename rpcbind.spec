Summary:	Universal Addresses to RPC Program Number Mapper
Name:		rpcbind
Version:	1.2.6
Release:	2
License:	BSD
Group:		System/Servers
Url:		https://rpcbind.sourceforge.net/
Source0:	http://downloads.sourceforge.net/rpcbind/%{name}-%{version}.tar.bz2
Source1:	rpcbind.sysconfig
Source2:	sbin.rpcbind.apparmor
Source3:	%{name}.sysusers
Patch1:		rpcbind-0.2.3-systemd-envfile.patch
Patch2:		rpcbind-0.2.3-systemd-tmpfiles.patch
Patch3:		rpcbind-0.2.4-runstatdir.patch
Patch4:		rpcbind-0.2.4-systemd-service.patch
Patch5:		rpcbind-0.2.4-systemd-rundir.patch
BuildRequires:	quota-devel
BuildRequires:	pkgconfig(libtirpc)
BuildRequires:	pkgconfig(libsystemd)
BuildRequires:	systemd-rpm-macros
Requires(pre):	systemd
%systemd_requires

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
	--with-systemdtmpfilesdir=%{_tmpfilesdir} \

%make_build all

%install
mkdir -p %{buildroot}{%{_bindir},%{_sysconfdir}/sysconfig}
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

install -Dpm 644 %{SOURCE3} %{buildroot}%{_sysusersdir}/%{name}.conf

%pre
%sysusers_create_package %{name}.conf %{SOURCE3}

%posttrans
# if we have apparmor installed, reload if it's being used
if [ -x /sbin/apparmor_parser ]; then
	/sbin/service apparmor condreload
fi

%post
%systemd_post rpcbind.socket

%preun
%systemd_preun rpcbind.socket

%postun
%systemd_postun_with_restart rpcbind.socket

%files
%doc AUTHORS COPYING ChangeLog
%config(noreplace) %{_sysconfdir}/sysconfig/rpcbind
%config(noreplace) %{_sysconfdir}/apparmor.d/sbin.rpcbind
%{_sbindir}/rpcbind
%{_bindir}/rpcinfo
%{_tmpfilesdir}/rpcbind.conf
%{_mandir}/man8/*
%{_unitdir}/rpcbind.service
%{_unitdir}/rpcbind.socket
%{_presetdir}/86-%{name}.preset
%{_sysusersdir}/%{name}.conf
