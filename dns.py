from scapy.all import *
import socket

from scapy.layers.dns import DNS, DNSRR, DNSQR
from scapy.layers.inet import UDP, IP

cache = {"google.com": "8.8.8.8"}  # dictionary to store cached domain names and their IP addresses
dnsIP = "10.0.0.12"

# this file determines a dns server which holds a cache with website addresses as keys and ip's as a value
# while this dns server runs, if the website address is cached , it will send the appropriate ip to the sender
# else, if the website address is not cached , it will use "gethosybyname()" function that will return the appropriate
# ip, in this case, the block is surrounded by try and except for the case the function gets an error
def dns_responder(packet):
    if DNS in packet and packet[DNS].qr == 0:
        # Only respond to DNS query packets with no answers
        qname = packet[DNSQR].qname.decode('utf-8').rstrip('.')  # -null byte

        if qname in cache:
            # If the requested domain name is in the cache, return the cached IP address
            ipInfo = IP(src=dnsIP, dst=packet[IP].src)
            udpInfo = UDP(dport=packet[UDP].sport, sport=53)
            dnsInfo = DNS(id=packet[DNS].id, qd=packet[DNS].qd, an=DNSRR(rrname=qname, rdata=cache[qname]), qr=1)
            resp_pkt = ipInfo / udpInfo / dnsInfo
            send(resp_pkt, verbose=0)
        else:
            # If the requested domain name is not in the cache, perform a DNS lookup and cache the result
            try:
                ip = socket.gethostbyname(qname)
                cache[qname] = ip
                ipInfo = IP(src=dnsIP, dst=packet[IP].src)
                udpInfo = UDP(dport=packet[UDP].sport, sport=53)
                dnsInfo = DNS(id=packet[DNS].id, qd=packet[DNS].qd, an=DNSRR(rrname=qname, rdata=ip), qr=1)
                resp_pkt = ipInfo / udpInfo / dnsInfo
                send(resp_pkt, verbose=0)
            except socket.gaierror:
                # If the DNS lookup fails, return a response with no answers
                ipInfo = IP(src=dnsIP, dst=packet[IP].src)
                udpInfo = UDP(dport=packet[UDP].sport, sport=53)
                dnsInfo = DNS(id=packet[DNS].id, qd=packet[DNS].qd)
                resp_pkt = ipInfo / udpInfo / dnsInfo
                send(resp_pkt, verbose=0)


if __name__ == "__main__":
    sniff(filter="udp port 53", iface="enp0s3", prn=dns_responder)
