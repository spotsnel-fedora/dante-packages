%if 0%{?el7}
%define dist .el7
%endif

#define pre pre2
%global  __global_cflags -O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector-strong --param=ssp-buffer-size=4 %{_hardened_cflags}
%{!?_unitdir: %global _unitdir /lib/systemd/system}

Name:		dante
Version:	1.4.3
Release:	1%{?dist}
Summary:	A free SOCKS v4/v5 client implementation

Packager:	gbraad <me@gbraad.nl>
Vendor:		SpotSnel, https://spotsnel.nl

Group:		Networking/Utilities
License:	BSD-type
URL:		http://www.inet.no/dante/
Source0:	ftp://ftp.inet.no/pub/socks/%{name}-%{version}%{?pre:-%{pre}}.tar.gz
Source1:	dante.service
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

BuildRequires:	pam-devel, bison, flex, glibc-headers
BuildRequires:	gcc

Requires(post):		systemd-units
Requires(preun):	systemd-units
Requires(postun):	systemd-units

%description
Dante is a free implementation of the SOCKS proxy protocol, version 4,
and version 5 (rfc1928). It can be used as a firewall between
networks. It is being developed by Inferno Nettverk A/S, a Norwegian
consulting company. Commercial support is available.

This package contains the dynamic libraries required to "socksify"
existing applications, allowing them to automatically use the SOCKS
protocol.

%package server
Summary:	A free SOCKS v4/v5 server implementation
Group:		System Environment/Daemons
Requires:	dante

%description server
This package contains "sockd", the SOCKS proxy daemon and its
documentation.  This is the server part of the Dante SOCKS proxy
package and allows SOCKS clients to connect through it to the external
network.

%package devel
Summary:	development libraries for SOCKS
Group:		Development/Libraries
Requires:	dante

%description devel
Additional libraries required to compile programs that use SOCKS.

%prep
%setup -q -n %{name}-%{version}%{?pre:-%{pre}}

%build
LDFLAGS="$LDFLAGS -lm"
%configure \
	--without-glibc-secure \
	--enable-shared \
	--disable-static

make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

#set library as executable - prevent ldd from complaining
chmod +x ${RPM_BUILD_ROOT}%{_libdir}/*.so.*.*
install -D -m0644 example/socks-simple.conf $RPM_BUILD_ROOT%{_sysconfdir}/socks.conf
install -D -m0644 example/sockd.conf $RPM_BUILD_ROOT%{_sysconfdir}/sockd.conf
install -D -m0644 %{SOURCE1} $RPM_BUILD_ROOT%{_unitdir}/sockd.service

find %{buildroot} -regex ".*\.la$" | xargs rm -f --

%clean
rm -rf $RPM_BUILD_ROOT

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%post server
%systemd_post sockd.service

%preun server
%systemd_preun suricata.service

%postun server
%systemd_postun_with_restart sockd.service

%files
%defattr(-,root,root,0755)
%doc BUGS CREDITS NEWS README* SUPPORT doc/README* example/socks.conf example/socks-simple-withoutnameserver.conf example/sockd.conf example/socks-simple.conf
%{!?_licensedir:%global license %%doc}
%license LICENSE
%config %{_sysconfdir}/socks.conf
%{_libdir}/libsocks.so.0.1.1
%{_libdir}/libsocks.so.0
%{_libdir}/libsocks.so
%{_libdir}/libdsocks.so
%{_bindir}/socksify
%{_mandir}/man1/socksify.1*
%{_mandir}/man5/socks.conf.5*

%files server
%defattr(-, root, root, 0755)
%config %{_sysconfdir}/sockd.conf
%{_unitdir}/sockd.service
%{_sbindir}/sockd
%{_mandir}/man5/sockd.conf.5*
%{_mandir}/man8/sockd.8*

%files devel
%defattr(-, root, root, 0755)
%doc INSTALL doc/rfc* doc/SOCKS4.protocol
%{_includedir}/socks.h

%changelog
* Sat Apr 01 2023 gbraad <me@gbraad.nl> - 1.4.3-1
- Update to 1.4.3
- remove init-script

* Sat Jul 07 2018 momo-i <webmaster@momo-i.org> - 1.4.2-1
- Update to 1.4.2

* Thu Sep 03 2015 momo-i <webmaster@momo-i.org> - 1.4.1-5
- Update dist for centos7

* Mon Aug 10 2015 momo-i <webmaster@momo-i.org> - 1.4.1-4
- Rebuilt for fc23

* Wed Apr 15 2015 momo-i <webmaster@momo-i.org> - 1.4.1-3
- Rebuilt for fc22

* Tue Oct 21 2014 momo-i <webmaster@momo-i.org> - 1.4.1-2
- Update to 1.4.1

* Fri Feb 14 2014 momo-i <webmaster@momo-i.org> - 1.4.0-2
- update spec file.

* Wed Feb 12 2014 momo-i <webmaster@momo-i.org> - 1.4.0-1
- Update to 1.4.0
- rewrite spec file for fedora.

* Fri Oct 18 2013 momo-i <webmaster@momo-i.org> - 1.4.0-pre2-1
- Update to 1.4.0-pre2

* Wed Dec 07 2011 momo-i <webmaster@momo-i.org> - 1.3.2-1
- Initial rpm release.
