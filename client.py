from time import sleep

from scapy.all import *
from scapy.layers.dhcp import *

macaddr = "02:42:02:8c:72:a8"


def generate_dhcp_discover():
    # creating necessary information for the request:
    # ethInfo is the ethernet protocol information,needed for the link layer,dst mac address is set to broadcast address
    ethInfo = Ether(dst="ff:ff:ff:ff:ff:ff")

    # udpInfo is the udp protocol information , needed for the transport layer , src port is 68 as fit to dhcp request
    udpInfo = UDP(sport=68, dport=67)

    # bootpInfo is the boostrap protocol information , needed for the network layer and service
    # the dhcp for lookup for a free address, op is 1 because it is a request
    bootpInfo = BOOTP(op=1, chaddr=macaddr, xid=1)

    # ipInfo is the internet protocol information, needed for the network layer, dst is the broadcast address
    ipInfo = IP(src="0.0.0.0", dst="255.255.255.255")

    # dhcpInfo is the user datagram protocol information needed for the network layer,
    # currently looking for particular addr
    dhcpInfo = DHCP(options=[("message-type", "discover"), "end"])

    # this is the whole packet (sent to everyone)
    dhcp_discover = ethInfo / ipInfo / udpInfo / bootpInfo / dhcpInfo

    # Send the packet and capture the response
    sendp(dhcp_discover, iface="enp0s3")


def handle_dhcp_response(dhcp_offer):
    offered_server_id = dhcp_offer[DHCP].options[1][1]
    offered_ip_address = dhcp_offer[BOOTP].yiaddr
    if dhcp_offer:
        print("IP address offered by the DHCP server:", offered_server_id)
        print("IP address offered for the DNS server:", offered_ip_address)
    else:
        print("No response received from the DHCP server")

    dhcp_mac_addr = dhcp_offer[Ether].src
    transaction_id = dhcp_offer[BOOTP].xid
    ethInfo = Ether(src=macaddr, dst=dhcp_mac_addr)
    udpInfo = UDP(sport=68, dport=67)
    ipInfo = IP(src="0.0.0.0", dst=dhcp_offer[IP].src)
    bootpInfo = BOOTP(op=2, yiaddr=offered_ip_address, siaddr="0.0.0.0",
                      chaddr=dhcp_mac_addr, xid=transaction_id)
    dhcpInfo = DHCP(options=[("message-type", "request"),
                             ("server id", offered_server_id),
                             ("ip address", offered_ip_address),
                             "end"])
    dhcp_request = ethInfo / ipInfo / udpInfo / bootpInfo / dhcpInfo
    sleep(1)
    sendp(dhcp_request, iface="enp0s3")


if __name__ == "__main__":
    generate_dhcp_discover()
    sniff(filter="udp and (port 67 or port 68)", iface="enp0s3", count=1,
          prn=handle_dhcp_response)
    ans = sniff(filter="udp and (port 67 or port 68)", iface="enp0s3", count=1)
    pack = ans[0]
    dnsIp = clientIP = None

    # if ack received so we completed the dhcp progress
    if pack[DHCP].options[0][1] == 5:
        dnsIp = pack[DHCP].options[1][1]
        clientIP = pack[BOOTP].yiaddr
    else:
        raise ValueError("try again")


