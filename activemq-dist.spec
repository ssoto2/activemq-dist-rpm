%global pkgname apache-%{project}
%global project activemq
%global __os_install_post /usr/lib/rpm/brp-compress %{nil}

%define __requires_exclude_from ^.*\\.jar$
%define __provides_exclude_from ^.*\\.jar$
%define debug_package %{nil}
%define amqhome /usr/share/%{project}

Name:           activemq-dist
Version:        5.15.8
Release:        1%{?dist}
Summary:        ActiveMQ Messaging Broker
Group:          Networking/Daemons
License:        ASL 2.0
URL:            http://activemq.apache.org/
Source0:        https://ftp.halifax.rwth-aachen.de/apache/activemq/%{version}/%{pkgname}-%{version}-bin.tar.gz
Source1:        https://raw.githubusercontent.com/ssoto2/activemq-dist-rpm/5.15.8/activemq-conf
Source2:        https://raw.githubusercontent.com/ssoto2/activemq-dist-rpm/5.15.8/activemq.logrotate
Patch0:         https://raw.githubusercontent.com/ssoto2/activemq-dist-rpm/5.15.8/init.d.patch
Patch1:         https://raw.githubusercontent.com/ssoto2/activemq-dist-rpm/5.15.8/wrapper.conf.patch
Patch2:         https://raw.githubusercontent.com/ssoto2/activemq-dist-rpm/5.15.8/log4j.patch
BuildRoot:      %{_tmppath}/%{pkgname}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  systemd
Requires:       java-headless >= 1:1.8.0
Requires:       which

%package client
Summary: Client jar for Apache ActiveMQ
Group:       System
%description client
Client jar for Apache ActiveMQ

%description
ActiveMQ Messaging Broker

%prep
%setup -q -n %{pkgname}-%{version}
%patch0 -p1
%patch1 -p1
%patch2 -p1


%build
/bin/true

%install
# BUILD HOME DIRECTORY
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{amqhome}

# SETUP HOME DIRECTORY
mv bin lib webapps $RPM_BUILD_ROOT%{amqhome}

# SETUP CONFIGURATIONS DIRECTORY
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}
mv conf $RPM_BUILD_ROOT%{_sysconfdir}/activemq
mv $RPM_BUILD_ROOT%{amqhome}/bin/linux-x86-64/wrapper.conf $RPM_BUILD_ROOT%{_sysconfdir}/activemq
ln -s %{_sysconfdir}/activemq $RPM_BUILD_ROOT%{amqhome}/conf

# SETUP LOGGING DIRECTORY
mkdir -p $RPM_BUILD_ROOT/var/log/activemq
ln -s /var/log/activemq $RPM_BUILD_ROOT%{amqhome}/log

# SETUP DATA DIRECTORY
mkdir -p $RPM_BUILD_ROOT/var/lib/activemq/data
ln -s /var/lib/activemq/data $RPM_BUILD_ROOT%{amqhome}/data

# SETUP SYSTEM FILES
mkdir -p $RPM_BUILD_ROOT/etc/init.d
mkdir -p $RPM_BUILD_ROOT/var/run/activemq
mv $RPM_BUILD_ROOT%{amqhome}/bin/linux-x86-64/activemq $RPM_BUILD_ROOT/etc/init.d

# SETUP LIBRARY DIRECTORY
mkdir -p $RPM_BUILD_ROOT%_libdir/%{project}
mv $RPM_BUILD_ROOT%{amqhome}/bin/linux-x86-64 $RPM_BUILD_ROOT%_libdir/%{project}/linux
ln -s %{_libdir}/%{project}/linux $RPM_BUILD_ROOT%{amqhome}/bin/linux-x86-64

# SETUP TMP DIRECTORY
mkdir -p $RPM_BUILD_ROOT%{amqhome}/tmp

# SETUP BINARY FILES
mkdir -p $RPM_BUILD_ROOT/usr/bin
ln -s %{amqhome}/bin/activemq-admin $RPM_BUILD_ROOT/usr/bin/activemq-admin
ln -s %{amqhome}/bin/activemq       $RPM_BUILD_ROOT/usr/bin/activemq

# SET UP JAR FILES
install -D -m 0644 activemq-all-%{version}.jar $RPM_BUILD_ROOT%{_javadir}/activemq-all-%{version}.jar
chmod a-x $RPM_BUILD_ROOT%{_javadir}/*
pushd %{buildroot}%{_javadir}
	for jar in *-%{version}*
   	do
      		ln -sf ${jar} `echo $jar | sed  "s|-%{version}||g"`
   	done
popd

# INSTALL FILES
install -D -m 0644 %{SOURCE1}  $RPM_BUILD_ROOT%{_sysconfdir}/activemq.conf
install -p -D -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

# CLEANUP 
rm -rf $RPM_BUILD_ROOT%{amqhome}/bin/linux-x86-32
rm -rf $RPM_BUILD_ROOT%{amqhome}/bin/macosx
#rm $RPM_BUILD_ROOT%{amqhome}/bin/wrapper.jar


# FIX UP PERMISSIONS (rpmlint complains)
find $RPM_BUILD_ROOT%{amqhome}/webapps -executable -type f -exec chmod -x '{}' \;


# DISABLE JAVA RMI
sed -i 's/^ACTIVEMQ_SUNJMX_START=/#ACTIVEMQ_SUNJMX_START=/' $RPM_BUILD_ROOT%{amqhome}/bin/env

# FIX DEFAULT CONNECTIONS
sed -i 's_\(<transportConnector.*/>\)_<!--\1-->_' \
   $RPM_BUILD_ROOT%{_sysconfdir}/activemq/activemq.xml


%clean
rm -rf $RPM_BUILD_ROOT

%pre
# Add the "activemq" user and group
# we need a shell to be able to use su - later
getent group %{project} >/dev/null || groupadd -r %{project}
getent passwd %{project} >/dev/null || \
/usr/sbin/useradd -g %{project} -s /bin/bash -r -c "Apache Activemq" \
        -d /usr/share/activemq activemq &>/dev/null || :

%post


%preun


%postun



%files
%defattr(-,root,root,-)
%doc LICENSE NOTICE README.txt docs/
%{amqhome}*
%_libdir/%{project}
/usr/bin/activemq
/usr/bin/activemq-admin
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%config(noreplace) %{_sysconfdir}/activemq/*
%config(noreplace) %{_sysconfdir}/activemq.conf
%attr(0755,root,root) /etc/init.d/activemq
%attr(755,activemq,activemq) %dir /var/log/activemq
%attr(755,activemq,activemq)  /var/lib/activemq
%attr(755,activemq,activemq) %dir /var/run/activemq

%files client
%defattr(-,root,root,-)
%doc LICENSE NOTICE README.txt docs/
%{_javadir}

%changelog
* Sat Dec 08 2018 Shauna Soto <ssoto@emich.edu> - 5.15.8-1
- Made platform specific
- enabled webui by default

* Sat Dec 08 2018 Lars Kiesow <lkiesow@uos.de> - 5.15.8-1
- Update to 5.15.8

* Sun Nov 11 2018 Lars Kiesow <lkiesow@uos.de> 5.15.7-1
- Update to 5.15.7

* Wed May 30 2018 Lars Kiesow <lkiesow@uos.de> 5.15.2-1
- Update to 5.15.4

* Thu Aug 03 2017 Lars Kiesow <lkiesow@uos.de> 5.15.0-1
- Update to ActiveMQ 5.15.0

* Fri Mar 17 2017 Lars Kiesow <lkiesow@uos.de> 5.14.4-1
- Update to ActiveMQ 5.14.4

* Mon Nov 14 2016 Lars Kiesow <lkiesow@uos.de> 5.14.1-2
- Fix several open ports

* Mon Oct 24 2016 Lars Kiesow <lkiesow@uos.de> 5.14.1-1
- Update to ActiveMQ 5.14.1
- Fixed systemd unit fiöe

* Wed Aug 17 2016 Lars Kiesow <lkiesow@uos.de> 5.14.0-1
- Update to ActiveMQ 5.14.0

* Wed Jul 13 2016 Lars Kiesow <lkiesow@uos.de> - 5.13.3-1
- Update to 5.13.3

* Fri Jan  8 2016 Lars Kiesow <lkiesow@uos.de> - 5.12.1-1
- Update to 5.12.1

* Thu Jan  7 2016 Lars Kiesow <lkiesow@uos.de> - 5.11.1-7
- Switch requirement to java-headless

* Tue Jun 23 2015 Lars Kiesow <lkiesow@uos.de> - 5.11.1-6
- Fix Java dependency generator problem

* Mon Jun 15 2015 Lars Kiesow <lkiesow@uos.de> - 5.11.1-5
- Fixed several rpmline warnings
- Added logrotation

* Thu Jun 11 2015 Lars Kiesow <lkiesow@uos.de> - 5.11.1-4
- Switched to Systemd

* Fri Apr 17 2015 Lars Kiesow <lkiesow@uos.de> - 5.11.1-3
- Fixed library linkes for wrapper

* Sun Apr  5 2015 Lars Kiesow <lkiesow@uos.de> - 5.11.1-1
- Update to 5.11.1

* Mon Feb 16 2015 Lars Kiesow <lkiesow@uos.de> - 5.11.0-1
- Update to 5.11.0

* Thu Apr 11 2013 Matthias Saou <matthias@saou.eu> 5.8.0-1
- Update to 5.8.0.

* Thu Nov 08 2012 Brenton Leanhardt <bleanhar@redhat.com> - 5.4.2-3%{?dist}
- Specifying we need java 1:1.6.0

* Thu Jan 06 2011 James Casey <james.casey@cern.ch> - 5.4.2-1%{?dist}
- rebuild for 5.4.2

* Sun Nov 07 2010 James Casey <jamesc.000@gmail.com> - 5.4.1-1%{?dist}
- rebuild for 5.4.1

* Tue May 18 2010 James Casey <james.casey@cern.ch> - 5.4-1%{?dist}
- rebuild for 5.4

* Tue May 18 2010 James Casey <james.casey@cern.ch> - 5.3.2-3%{?dist}
- Fix bug where /var/lib/activemq/data would not be installed

* Tue May 18 2010 James Casey <james.casey@cern.ch> - 5.3.2-2%{?dist}
- Rename package to activemq from apache-activemq
- Integrated comments from Marc Schöchlin
- moved /var/cache/activemq to /var/lib/activemq
- added dependency on java
- Fixed file permissions (executable bit set on many files)
- Fixed rpmlint errors
- move platform dependant binaries to /usr/lib

* Fri May 07 2010 James Casey <james.casey@cern.ch> - 5.3.2-1
- First version of specfile

