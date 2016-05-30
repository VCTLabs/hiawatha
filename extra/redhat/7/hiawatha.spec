Name:           hiawatha
Version:        10.2
Release:        0
Summary:        Hiawatha, an advanced and secure webserver for Unix
Group:          Applications/Internet
License:        GPLv2
URL:            https://www.hiawatha-webserver.org/
Source0:        https://www.hiawatha-webserver.org/files/%{name}-%{version}.tar.gz
Source1:        hiawatha.service
Patch0:         hiawatha-nobody99.patch

BuildRoot:      %{_topdir}/BUILDROOT/
BuildRequires:  cmake,make,gcc,glibc-devel,zlib-devel,libxml2-devel,libxslt-devel
Requires:       libxml2,libxslt

%description
Hiawatha is a webserver with the three key attributes: secure, easy-to-use, and lightweight.

%prep
%setup -q
%patch0 -p1

%build
CFLAGS="${CFLAGS:-%optflags}" ; export CFLAGS
CXXFLAGS="${CXXFLAGS:-%optflags}" ; export CXXFLAGS
FFLAGS="${FFLAGS:-%optflags}" ; export FFLAGS
cmake -DCMAKE_INSTALL_PREFIX="" -DCMAKE_INSTALL_LIBDIR=%{_libdir} \
      -DCMAKE_INSTALL_BINDIR=%{_bindir} -DCMAKE_INSTALL_SBINDIR=%{_sbindir} \
      -DCMAKE_INSTALL_SYSCONFDIR=%{_sysconfdir} -DCMAKE_INSTALL_MANDIR=%{_mandir} \
      -DENABLE_TOMAHAWK=on -DENABLE_MONITOR=on
%__make %{?_smp_mflags}

%install
rm -rf %{buildroot}
mkdir -p  %{buildroot}
%__make install DESTDIR=%{buildroot}
mkdir -p %{buildroot}%{_defaultdocdir}/hiawatha
cp ChangeLog %{buildroot}%{_defaultdocdir}/hiawatha
mkdir -p %{buildroot}%{_initrddir}
cp extra/debian/init.d/hiawatha %{buildroot}%{_initrddir}
mkdir -p %{buildroot}%{_sysconfdir}/logrotate.d
cp %{_sourcedir}/hiawatha.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/hiawatha
mkdir -p %{buildroot}%{_unitdir}
cp %{_sourcedir}/hiawatha.service %{buildroot}%{_unitdir}/hiawatha.service

# separate subdir for custom configs
mkdir -p %{buildroot}%{_sysconfdir}/hiawatha/conf.d
sed -i "s/#ServerId/ServerId/" %{buildroot}%{_sysconfdir}/hiawatha/hiawatha.conf
cat <<EOF >> %{buildroot}%{_sysconfdir}/hiawatha/hiawatha.conf

# custom configs (e.g. virtual servers) can go in files under conf.d
include conf.d/
EOF

%pre
getent group www-data >/dev/null || groupadd -r www-data
getent passwd www-data >/dev/null || \
	useradd -r -g www-data -d /var/www -s /sbin/nologin \
	-c "Web server user" www-data
%post
%systemd_post hiawatha.service

%preun
%systemd_preun hiawatha.service

%postun
%systemd_postun_with_restart hiawatha.service

%clean
rm -rf %{buildroot}

%files
%attr(555, root, root) %{_bindir}/
%attr(555, root, root) %{_sbindir}/
%attr(-, root, root) %{_libdir}/hiawatha/
%attr(-, root, root) %{_mandir}/
%attr(-, root, root) %{_localstatedir}/www/hiawatha/
%attr(-, root, root) %{_defaultdocdir}/hiawatha/
%attr(-, root, root) %{_initrddir}/
%attr(-, root, root) %{_unitdir}/
%attr(-, www-data, www-data) %{_localstatedir}/log/hiawatha/
%config %{_sysconfdir}/hiawatha
%config %{_sysconfdir}/logrotate.d/hiawatha

%changelog
* Mon May 23 2016 S. Lockwood-Childs <sjl@vctlabs.com>
- adapted for CentOS 7
