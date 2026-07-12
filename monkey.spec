Summary:	A fast and lightweight web server for Linux
Summary(pl.UTF-8):	Szybki i lekki serwer WWW dla Linuksa
Name:		monkey
Version:	1.8.5
Release:	1
License:	Apache v2
Group:		Networking/Daemons
Source0:	https://github.com/monkey/monkey/archive/refs/tags/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	8b8d68b8517163443abdf4718a3855c3
Source1:	%{name}.service
Source2:	%{name}.tmpfiles
Source3:	monkeyd.init
Patch0:		%{name}-cmake-install-paths.patch
URL:		https://monkey-project.com/
BuildRequires:	cmake >= 3.20
BuildRequires:	rpmbuild(macros) >= 1.268
Requires(post,preun):	/sbin/chkconfig
Requires(post,preun,postun):	systemd-units >= 38
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	systemd-units >= 38
Provides:	webserver
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/monkey
%define		_webdir		/home/services/monkey

%description
Monkey is a fast and lightweight web server for Linux. It has been
designed to be very scalable with low memory and CPU consumption, the
perfect solution for embedded and high production environments.

%description -l pl.UTF-8
Monkey to szybki i lekki serwer WWW dla Linuksa. Został zaprojektowany
jako bardzo skalowalny przy niskim zużyciu pamięci i procesora - idealne
rozwiązanie dla środowisk wbudowanych i produkcyjnych.

%package devel
Summary:	Header files for Monkey HTTP server plugin development
Summary(pl.UTF-8):	Pliki nagłówkowe do tworzenia wtyczek dla serwera Monkey
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
Header files for building plugins against the Monkey HTTP server.

%description devel -l pl.UTF-8
Pliki nagłówkowe do tworzenia wtyczek dla serwera HTTP Monkey.

%prep
%setup -q
%patch -P0 -p1

%build
install -d build
cd build
%cmake .. \
	-DCMAKE_INSTALL_SBINDIR=%{_sbindir} \
	-DINSTALL_SYSCONFDIR=%{_sysconfdir} \
	-DINSTALL_WEBROOTDIR=%{_webdir} \
	-DINSTALL_LOGDIR=%{_var}/log/monkey \
	-DPID_PATH=%{_var}/run/monkey \
	-DDEFAULT_USER=http \
	-DDEFAULT_PORT=80

%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} -C build install DESTDIR=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT{%{systemdunitdir},%{systemdtmpfilesdir},%{_webdir},/etc/rc.d/init.d}
cp -p %{SOURCE1} $RPM_BUILD_ROOT%{systemdunitdir}/monkey.service
cp -p %{SOURCE2} $RPM_BUILD_ROOT%{systemdtmpfilesdir}/monkey.conf
install -p %{SOURCE3} $RPM_BUILD_ROOT/etc/rc.d/init.d/monkey

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -r -g 51 http
%useradd -r -u 214 -d %{_webdir} -s /bin/false -c "Monkey HTTP Server" -g http monkey

%post
/sbin/chkconfig --add monkey
%systemd_post monkey.service

%preun
if [ "$1" = "0" ]; then
	%service monkey stop
	/sbin/chkconfig --del monkey
fi
%systemd_preun monkey.service

%postun
%systemd_reload

%files
%defattr(644,root,root,755)
%doc ChangeLog README.md
%dir %{_sysconfdir}
%dir %{_sysconfdir}/plugins
%dir %{_sysconfdir}/sites
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/monkey.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/monkey.mime
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/plugins.load
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/sites/default
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/plugins/dirlisting/dirhtml.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/plugins/mandril/mandril.conf
%{_sysconfdir}/plugins/dirlisting/themes
%attr(755,root,root) %{_sbindir}/monkey
%attr(755,root,root) %{_libdir}/monkey-dirlisting.so
%attr(755,root,root) %{_libdir}/monkey-mandril.so
%{systemdunitdir}/monkey.service
%attr(754,root,root) /etc/rc.d/init.d/monkey
%{_mandir}/man1/monkey.1*
%dir %attr(750,monkey,http) %{_var}/log/monkey
%dir %attr(750,monkey,http) %{_var}/run/monkey
%{systemdtmpfilesdir}/monkey.conf
%dir %{_webdir}

%files devel
%defattr(644,root,root,755)
%{_includedir}/monkey
