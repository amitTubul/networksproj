import urllib.request
from time import sleep
from scapy.all import *
from scapy.layers.dhcp import *
from scapy.layers.dns import DNS, DNSQR, DNSRR
from scapy.layers.http import HTTPResponse
from scapy.layers.inet import TCP

macaddr = "02:42:02:8c:72:a8"
http_domainName = "http_server.com"
http_port = 80
client_port = 5000


# this function generates a dhcp discover query and broadcast it over udp
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


# this function handles dhcp response from a dhcp so that it requests the ip from dhcp offer
# from the dhcp server over udp
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


# this function sends a dns query to the dns server and then sniffs for a query response from the dns server
# notice that we use a udp packet
def send_dns_query(clientIp, dnsIp, domainName):
    ipInfo = IP(src=clientIp, dst=dnsIp)
    udpInfo = UDP(sport=53, dport=53)
    # qd is the requested website address , using DNSQR function for a dns queries, qr=0 because it is a query
    dnsInfo = DNS(qd=DNSQR(qname=domainName), qr=0)
    query_pkt = ipInfo / udpInfo / dnsInfo

    send(query_pkt, verbose=0)
    response = sniff(filter=f'host {clientIp}', iface="enp0s3", count=1)[0]

    if response and response.haslayer(DNSRR):
        print(f"The IP address of {domainName} is {response[DNSRR].rdata}")
        return response[DNSRR].rdata
    else:
        print(f"DNS lookup for {domainName} failed.")
        return None


def http_server_connection(server_ip, dnsIp, clientIp):
    server_address = (server_ip, http_port)

    # Create client socket and connect to server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server_address)

    # Create HTTP GET request
    http_get_request = f"GET /example.txt HTTP/1.1\r\nHost: {server_ip}\r\n\r\n"

    # Send HTTP GET request to server
    client_socket.send(http_get_request.encode())

    # Receive and print response from server
    response = client_socket.recv(1024)
    response_str = response.decode()
    if re.search('302', response_str):
        # Handle redirect
        match = re.search(r'Location: (.*?)\r\n', response_str)
        if match:
            redirect_url = match.group(1)
            print(f"Redirected to {redirect_url}\nconnecting dns...")
            redirected_http_ip = send_dns_query(clientIp, dnsIp, redirect_url)
            http_server_connection(redirected_http_ip, dnsIp, clientIp)
    elif re.search('200', response_str):
        print(response_str)

    # Close client socket
    client_socket.close()


if __name__ == "__main__":
    # generate_dhcp_discover()
    # sniff(filter="udp and (port 67 or port 68)", iface="enp0s3", count=1,
    #       prn=handle_dhcp_response)
    # ans = sniff(filter="udp and (port 67 or port 68)", iface="enp0s3", count=1)
    # pack = ans[0]
    #
    # # if ack received so we completed the dhcp progress
    # if pack[DHCP].options[0][1] != 5:
    #     raise ValueError("try again")
    #
    # dnsIp = pack[DHCP].options[1][1]
    # clientIp = pack[BOOTP].yiaddr
    # http_ip = send_dns_query(clientIp, dnsIp, http_domainName)

    # Set the URL of the server to download the file from
    clientIP = "10.0.0.11"
    dnsIP = "10.0.0.12"
    http_ip = "0.0.0.0"
    http_server_connection(http_ip, dnsIP, clientIP)
