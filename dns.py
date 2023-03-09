from scapy.all import *
import socket

from scapy.layers.dns import DNS, DNSRR, DNSQR
from scapy.layers.inet import UDP, IP
# dictionary to store cached domain names and their IP addresses
cache = {"http://http_server.com": "0.0.0.0", "http://redirected_http_server.com/example.txt": "10.0.2.15"}
dnsIP = "10.0.0.12"


# this file determines a dns server which holds a cache with website addresses as keys and ip's as a value
# while this dns server runs, if the website address is cached , it will send the appropriate ip to the sender
# else, if the website address is not cached , it will use "gethosybyname()" function that will return the appropriate
# ip, in this case, the block is surrounded by try and except for the case the function gets an error
def dns_responder(pack):
    # the client sends a packet with qr=0, which tell it is a request
    if DNS in pack and pack[DNS].qr == 0:
        # taking the requested website address and deleting the last byte because it is a null byte became '.'
        qname = pack[DNSQR].qname.decode('utf-8').rstrip('.')
        print(qname)
        if qname in cache:
            # If the requested domain name is in the cache, return the cached IP address
            # building a packet layer by layer with ip, udp and dns and sending the response, src and dst ports is 53
            ipInfo = IP(src=dnsIP, dst=pack[IP].src)
            udpInfo = UDP(dport=pack[UDP].sport, sport=53)
            # 'id' is the id of the dns query, we reuse it for the connections safety
            # 'qd' is the website address asked, 'an' is the answer for the client, for that we use DNSRR,
            # 'qr' is 1 because it is a query response
            dnsInfo = DNS(id=pack[DNS].id, qd=pack[DNS].qd, an=DNSRR(rrname=qname, rdata=cache[qname]), qr=1)
            resp_pkt = ipInfo / udpInfo / dnsInfo
            send(resp_pkt, verbose=0)
        else:
            # If the requested domain name is not in the cache, perform a DNS lookup and cache the result
            try:
                ip = socket.gethostbyname(qname)
                cache[qname] = ip
                ipInfo = IP(src=dnsIP, dst=pack[IP].src)
                udpInfo = UDP(dport=pack[UDP].sport, sport=53)
                dnsInfo = DNS(id=pack[DNS].id, qd=pack[DNS].qd, an=DNSRR(rrname=qname, rdata=ip), qr=1)  # new 'an'
                resp_pkt = ipInfo / udpInfo / dnsInfo
                send(resp_pkt, verbose=0)
            except socket.gaierror:
                # If the DNS lookup fails, return a response with no answers
                ipInfo = IP(src=dnsIP, dst=pack[IP].src)
                udpInfo = UDP(dport=pack[UDP].sport, sport=53)
                dnsInfo = DNS(id=pack[DNS].id, qd=pack[DNS].qd)  # no 'an'
                resp_pkt = ipInfo / udpInfo / dnsInfo
                send(resp_pkt, verbose=0)


if __name__ == "__main__":
    sniff(filter="dst host 10.0.0.12", iface="enp0s3", prn=dns_responder)
