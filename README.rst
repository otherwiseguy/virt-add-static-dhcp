virt-add-static-dhcp
====================

A quick script to take an interface attached to a libvirt VM and add
a static DHCP IP for it to the appropriate libvirt network.

Usage:
# virt-add-static-dhcp <domain> <network> <ip>

Requires Python 2.7+ and the libvirt development libraries (e.g. libvirt-devel
on Red Hat systems)
