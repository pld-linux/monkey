Summary:	Small WebServer
Summary(pl):	Ma�y WebServer
Name:		monkey
Version:	0.8.2
Release:	0.2
Group:		Networking/Daemons
License:	GPL
Source0:	http://monkeyd.sourceforge.net/versions/%{name}-%{version}.tar.gz
# Source0-md5:	17dfa899380a578787a6a309b476c9fc
Source1:	%{name}d.init
Patch0:		%{name}-pld.patch
Patch1:		%{name}-security.patch
URL:		http://monkeyd.sourceforge.net/
PreReq:		rc-scripts
Requires(post,preun):	/sbin/chkconfig
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
Provides:	webserver
Provides:	httpd
Obsoletes:	httpd
Obsoletes:	webserver

%define		_bindir		/usr/sbin
%define		_sysconfdir	/etc/httpd
%define		httpdir		/home/services/httpd

%description
Monkey is a small WebServer written 100% in C.

%description -l pl
Monkey to ma�y WebServer napisany w 100% w j�zyku C.

%prep
%setup -q
%patch0 -p1
%patch1 -p1

%build
./configure \
	--cgibin=%{httpdir}/cgi-bin \
	--sysconfdir=%{_sysconfdir} \
	--datadir=%{httpdir}/html \
	--logdir=/var/log/monkey \
	--lang=en

%{__make} \
	CFLAGS="%{rpmcflags}"

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT/etc/rc.d/init.d
install -d $RPM_BUILD_ROOT%{_bindir} \
	$RPM_BUILD_ROOT%{_sysconfdir} \
	$RPM_BUILD_ROOT%{httpdir}/cgi-bin \
	$RPM_BUILD_ROOT%{httpdir}/html/{imgs,php,docs} \
	$RPM_BUILD_ROOT%{_var}/log/monkey

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/monkeyd
install bin/monkey $RPM_BUILD_ROOT%{_bindir}
install cgi-bin/* $RPM_BUILD_ROOT%{httpdir}/cgi-bin
install conf/*.* $RPM_BUILD_ROOT%{_sysconfdir}
install htdocs/*.* $RPM_BUILD_ROOT%{httpdir}/html
install htdocs/imgs/*.* $RPM_BUILD_ROOT%{httpdir}/html/imgs
install htdocs/php/*.* $RPM_BUILD_ROOT%{httpdir}/html/php
install htdocs/docs/*.* $RPM_BUILD_ROOT%{httpdir}/html/docs

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add monkey
if [ -f /var/lock/subsys/monkey ]; then
	/etc/rc.d/init.d/monkey restart 1>&2
else
	echo "Type \"/etc/rc.d/init.d/monkey start\" to start monkey." 1>&2
fi

%preun
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/monkey ]; then
		/etc/rc.d/init.d/monkey stop 1>&2
	fi
	/sbin/chkconfig --del monkey
fi

%files
%defattr(644,root,root,755)
%doc ChangeLog HowItWorks.txt README
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/*
%attr(755,root,root) %{_bindir}/*
%attr(754,root,root) /etc/rc.d/init.d/*
%attr(000,root,root) %{httpdir}/cgi-bin/*
# index.html would be replaced/removed with the package!!!
%{httpdir}/html/*
%{_var}/log/monkey
