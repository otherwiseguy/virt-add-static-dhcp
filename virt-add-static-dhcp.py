#!/usr/bin/env python
from __future__ import print_function
import argparse
import libvirt
import sys
import xml.etree.ElementTree as ET

ERR_NO_ERROR = 0
ERR_NO_CONNECT = 1
ERR_NO_DOMAIN = 2
ERR_NO_NETWORK = 3
ERR_NO_INTERFACE = 4
ERR_NO_ADD_IP = 5


def MACLookupByNetworkName(self, netname):
    root = ET.fromstring(self.XMLDesc())
    findstr = (
        "./devices/interface[@type='network']/source[@network='%s']/../mac" % (
            netname,))
    return root.find(findstr).attrib.get('address')


def addOrUpdateHost(self, mac, ip):
    cmd = libvirt.VIR_NETWORK_UPDATE_COMMAND_MODIFY
    section = libvirt.VIR_NETWORK_SECTION_IP_DHCP_HOST
    xml = "<host mac='%s' ip='%s'/>" % (mac, ip)
    flags = (libvirt.VIR_NETWORK_UPDATE_AFFECT_LIVE |
             libvirt.VIR_NETWORK_UPDATE_AFFECT_CONFIG)
    try:
        self.update(cmd, section, -1, xml, flags)
    except:
        cmd = libvirt.VIR_NETWORK_UPDATE_COMMAND_ADD_FIRST
        self.update(cmd, section, -1, xml, flags)

libvirt.virNetwork.addOrUpdateHost = addOrUpdateHost
libvirt.virDomain.MACLookupByNetworkName = MACLookupByNetworkName


def main():
    parser = argparse.ArgumentParser(
        description="Add/update a static DHCP address for a libvirt domain")
    parser.add_argument('domain', type=str, help="Libvirt domain name")
    parser.add_argument('network', type=str,
                        help="Libvirt network the domain's interface is on")
    parser.add_argument('ip', type=str,
                        help="The IP Address to assign to the interface")
    args = parser.parse_args()

    conn = libvirt.open(None)
    if conn is None:
        print('Failed to open connection to the hypervisor', file=sys.stderr)
        return ERR_NO_CONNECT

    try:
        dom = conn.lookupByName(args.domain)
    except:
        print('Failed to find the domain %s' % (args.domain,), file=sys.stderr)
        return ERR_NO_DOMAIN

    try:
        net = conn.networkLookupByName(args.network)
    except:
        print('Failed to find the network' % (args.network,), file=sys.stderr)
        return ERR_NO_NETWORK

    try:
        mac = dom.MACLookupByNetworkName(args.network)
    except:
        print("Could not find mac for %s network on %s" % (
            args.network, args.domain), file=sys.stderr)
        return ERR_NO_INTERFACE

    try:
        net.addOrUpdateHost(mac, args.ip)
    except:
        print("Could not add static DHCP entry for %s on %s" % (
            args.network, args.domain), file=sys.stderr)
        return ER_NO_ADD_IP

    return ERR_NO_ERROR

if __name__ == '__main__':
    sys.exit(main())
