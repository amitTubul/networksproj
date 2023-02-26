from time import sleep

from scapy.all import *
from scapy.layers.dhcp import *

clientIP = "10.0.0.11"
dnsIP = "10.0.0.12"
dhcpIp = "10.0.0.10"
macaddr = RandMAC()  # taking a random mac address


# this function handles a dhcp discover request from the client
def handle_dhcp_discover(pack):
    # this is the mac address of the client
    client_mac_addr = pack[Ether].src

    # Extract the transaction ID from the DHCP request
    transaction_id = pack[BOOTP].xid

    # creating necessary information for the response:
    # ethInfo is the ethernet protocol information,needed for the link layer,source mac address is random for safety
    ethInfo = Ether(src=macaddr, dst=client_mac_addr)

    # ipInfo is the internet protocol information,needed for the network layer,dst is the broadcast address
    ipInfo = IP(src=dhcpIp, dst="255.255.255.255")

    # udpInfo is the udp protocol information , needed for the transport layer , src port is 67 as fit to dhcp
    udpInfo = UDP(sport=67, dport=68)

    # bootpInfo is the boostrap protocol information , needed for the network layer and service
    # the dhcp for lookup for a free address, op is 2 because it is a reply
    bootpInfo = BOOTP(op=2, yiaddr=clientIP, siaddr="10.0.0.10",
                      chaddr=client_mac_addr, xid=transaction_id)

    # dhcpInfo is the user datagram protocol information , needed for the network layer
    dhcpInfo = DHCP(options=[("message-type", "offer"),
                             ("server_id", dnsIP),
                             ("subnet_mask", "255.255.255.0"),
                             ("router", dhcpIp),
                             ("lease_time", 86400),
                             "end"])

    # Create a DHCP response packet
    dhcp_response = ethInfo / ipInfo / udpInfo / bootpInfo / dhcpInfo

    # Send the DHCP response packet
    sleep(1)
    sendp(dhcp_response, iface="enp0s3")


# this function handles a dhcp response from the client, it will accept the ip request and send 'ack'
# notice that we use the senders information to send it back to the client
def handle_dhcp_response(pack):
    client_mac_addr = pack[Ether].src
    transaction_id = pack[BOOTP].xid
    ethInfo = Ether(src=macaddr, dst=client_mac_addr)
    ipInfo = IP(src=dhcpIp, dst="255.255.255.255")
    udpInfo = UDP(sport=67, dport=68)
    bootpInfo = BOOTP(op=2, yiaddr=clientIP, siaddr="10.0.0.10",
                      chaddr=client_mac_addr, xid=transaction_id)
    dhcpInfo = DHCP(options=[("message-type", "ack"),
                             ("server_id", dnsIP),
                             ("subnet_mask", "255.255.255.0"),
                             ("router", dhcpIp),
                             ("lease_time", 86400),
                             "end"])
    dhcp_ack = ethInfo / ipInfo / udpInfo / bootpInfo / dhcpInfo
    sleep(1)
    sendp(dhcp_ack, iface="enp0s3")


if __name__ == "__main__":
    sniff(filter="udp and (port 67 or port 68)", iface="enp0s3", prn=handle_dhcp_discover, count=1)
    sniff(filter="udp and (port 67 or port 68)", iface="enp0s3", prn=handle_dhcp_response, count=1)
