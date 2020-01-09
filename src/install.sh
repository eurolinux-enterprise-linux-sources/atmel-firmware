#!/bin/sh -e

if ! test -f /etc/hotplug/firmware.agent; then
    echo "/etc/hotplug/firmware.agent does not exist:"
    echo "please install an up-to-date hotplug package and re-try."
    exit 1
fi

if [ -d /lib/firmware ] ; then
    dest=/lib/firmware
    if [ -d /usr/lib/hotplug/firmware ] ; then
        echo "Both /usr/lib/hotplug/firmware and /lib/firmware exist:"
        echo "Assuming /lib/firmware is the correct choice."
    fi
else
    dest=/usr/lib/hotplug/firmware
    if [ ! -d /usr/lib/hotplug/firmware ] ; then
        echo "Neither /usr/lib/hotplug/firmware or /lib/firmware exist:"
        echo "Assuming /usr/lib/hotplug/firmware is the correct choice."
        mkdir -p /usr/lib/hotplug/firmware
    fi
fi 

echo "Installing new firmware files in $dest"
cp images/* $dest
cp images.usb/* $dest

echo "Installing firmware loader in /usr/sbin/atmel_fwl"
install -m 755 atmel_fwl.pl /usr/sbin/atmel_fwl
install -m 644 atmel_fwl.8 /usr/share/man/man8

if [ -f /etc/pcmcia/atmel.conf ] && \
    ! fgrep -q atmel_cs /etc/pcmcia/atmel.conf; then
    echo "Saving atmelwlandriver-derived atmel.conf as atmel.wlandriver"
    mv /etc/pcmcia/atmel.conf /etc/pcmcia/atmel.wlandriver
fi

echo "Installing PCMCIA config in /etc/pcmcia/atmel.conf"
install -m 644  atmel.conf /etc/pcmcia

if [ -f /var/run/cardmgr.pid ]; then
    echo "Re-reading PCMCIA configuration"
    kill -HUP `cat /var/run/cardmgr.pid`
fi
