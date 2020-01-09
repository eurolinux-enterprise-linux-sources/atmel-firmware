
%define release 1

##########################################################
#
#  Fedora detector from Tim Jackson, modified by srk to use target.
#
##########################################################
# For Fedore Core 3 firmware goes in /lib/firmware
# For other distros/releases we use /usr/lib/hotplug/firmware
%define fedoramajorver %(rpm -q --queryformat='%{VERSION}' fedora-release|cut -d. -f1)
%define fc3 %(if [ "%{fedoramajorver}" == "3" -o "%{_target}" == "fedora-linux" ];then echo 1;else echo 0;fi)


%if %{fc3}
%define firmware_dir /lib/firmware
%define extraver %{release}fc3
%else
%define firmware_dir /usr/lib/hotplug/firmware
%define extraver %{release}
%endif

###############################################################################
#
# General mumbojumbo
#
###############################################################################

Name: atmel-firmware
Version: 1.3
Release: %{extraver}
Copyright: Distributable
Group: System Environment/Kernel
Vendor: Simon Kelley
Packager: Simon Kelley
Distribution: LSB
URL: http://www.thekelleys.org.uk/atmel
Source0: %{name}-%{version}.tar.gz
Requires: hotplug
BuildRoot: /var/tmp/%{name}-%{version}
Summary: Firmware for Atmel at76c50x wireless network chips.
BuildArchitectures: noarch

%description
The drivers for Atmel at76c50x wireless network chips in the
Linux 2.6.x kernel and at http://at76c503a.berlios.de/ do not 
include the firmware and this firmware needs to be loaded by 
the host on most cards using these chips. 
This package provides the firmware images which 
should be automatically loaded as needed by the hotplug system. It also 
provides a small loader utility which can be used to accomplish the 
same thing when hotplug is not in use. 

###############################################################################
#
# Build
#
###############################################################################

%prep
echo "Building with firmware directory=%{firmware_dir}"
%setup -q

###############################################################################
#
# Install
#
###############################################################################

%install
rm -rf $RPM_BUILD_ROOT

mkdir -p -m 755 $RPM_BUILD_ROOT%{_sbindir}
mkdir -p -m 755 $RPM_BUILD_ROOT%{firmware_dir}
mkdir -p -m 755 $RPM_BUILD_ROOT%{_mandir}/man8
mkdir -p -m 755 $RPM_BUILD_ROOT%{_sysconfdir}/pcmcia

cp images/* $RPM_BUILD_ROOT%{firmware_dir}
cp images.usb/* $RPM_BUILD_ROOT%{firmware_dir}
cp atmel_fwl.pl $RPM_BUILD_ROOT%{_sbindir}/atmel_fwl
cp atmel_fwl.8 $RPM_BUILD_ROOT%{_mandir}/man8
gzip $RPM_BUILD_ROOT%{_mandir}/man8/atmel_fwl.8
cp atmel.conf $RPM_BUILD_ROOT%{_sysconfdir}/pcmcia

###############################################################################
#
# Clean up
#
###############################################################################

%clean
rm -rf $RPM_BUILD_ROOT


###############################################################################
#
# Post-install scriptlet
#
###############################################################################
%post
# Kick the cardmgr so it reads the new PCMCIA database entries.

if [ -f /var/run/cardmgr.pid ]; then
    kill -HUP `cat /var/run/cardmgr.pid`
fi

###############################################################################
#
# File list
#
###############################################################################

%files
%defattr(-,root,root)
%doc README COPYING 
%attr(0755,root,root) %{_sbindir}/atmel_fwl
%attr(0644,root,root) %{_mandir}/man8/atmel_fwl.8.gz
%attr(0644,root,root) %{_sysconfdir}/pcmcia/atmel.conf
%{firmware_dir}/*


##############################################################################
#
# Changelog
#
##############################################################################

%changelog
*Wed Jan 12 2005 Simon Kelley <simon@thekelleys.org.uk>
- Added LG LW2100N to atmel.conf
- Updated firmware license to Atmel's latest version.

*Sun Jan 09 2005 Simon Kelley <simon@thekelleys.org.uk>
- Use perl version of firmware loader, and make noarch

*Sun Jan 02 2005 Tim Jackson <tim@timj.co.uk>
- fixed firmware location for Fedora Core 3
- abstracted file locations

*Mon Aug 30 2004 Simon Kelley <simon@thekelleys.org.uk>
- added atmel_at76c505a-rfmd2958.bin
- added atmel_fwl.pl (to tarball)

*Thu May 13 2004 Simon Kelley <simon@thekelleys.org.uk>
- Updated license file.

*Sat Jan 17 2004 Simon Kelley <simon@thekelleys.org.uk>
- Renamed USB files to match PCMCIA ones.

*Wed Jan 14 2004 Simon Kelley <simon@thekelleys.org.uk>
- Added /etc/pcmcia/atmel.conf
- Added restart of PCMCIA system.
- Added USB firmware for Berlios driver.

* Sun Jan 4 2004 Simon Kelley <simon@thekelleys.org.uk>
- Initial version.
