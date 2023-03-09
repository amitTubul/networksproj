import re
import socket
from time import sleep


def tcp_server(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # SO_REUSEADDR is a socket option that allows the socket to be bound to an address that is already in use.
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        if ip == "0.0.0.0":
            response_head = "HTTP/1.1 302 Found\r\nLocation: http://redirected_http_server.com/example.txt\r\n\r\n"
        else:
            return -1

        address = (ip, port)
        server_socket.bind(address)
        server_socket.listen(1)
        while True:
            client_socket, address = server_socket.accept()
            data = client_socket.recv(1024)
            request = data.decode('utf-8')
            print(request)
            if request.startswith("GET"):
                client_socket.sendall(response_head.encode())
                client_socket.close()
                server_socket.close()
                return 1


def tcp_new_server(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # SO_REUSEADDR is a socket option that allows the socket to be bound to an address that is already in use.
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Read contents of example.txt file
        with open('example.txt', 'r') as file:
            response_body = file.read()
        if ip == "10.0.2.15":
            response_head = "HTTP/1.1 200 OK\r\nLocation: http://redirected_http_server.com/example.txt\r\n\r\n"
            response = response_head + response_body
        address = (ip, port)
        server_socket.bind(address)
        server_socket.listen(1)
        while True:
            client_socket, address = server_socket.accept()
            data = client_socket.recv(1024)
            request = data.decode('utf-8')
            print(request)
            if request.startswith("GET"):
                client_socket.sendall(response.encode())
                client_socket.close()
                server_socket.close()
                break


# def rudp_reliability(server_socket, server_address, options):
#     if options == 1:
#         while True:
#             response, address = server_socket.recv(1024)
#             response_str = response.decode('utf-8')
#             if re.search("SYN", response_str):
#                 ACK = "SYN, ACK"
#                 server_socket.send(ACK.encode(), server_address)
#                 return True
#
#     if options == 2:
#         ACK = "ACK"
#         server_socket.sendto(ACK.encode(), server_address)
#         while True:
#             response = server_socket.recv(1024)
#             response_str = response.decode('utf-8')
#             if re.search("ACK", response_str):
#                 return True
#
#     if options == 3:
#         while True:
#             response = server_socket.recv(1024)
#             response_str = response.decode('utf-8')
#             if re.search("FIN", response_str):
#                 fin_request = "FIN, ACK"
#                 server_socket.sendto(fin_request.encode(), server_address)
#                 return True
#
#     return False


def rudp_server(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        # SO_REUSEADDR is a socket option that allows the socket to be bound to an address that is already in use.
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        if ip == "0.0.0.0":
            response_head = "HTTP/1.1 302 Found\r\nLocation: http://redirected_http_server.com/example.txt\r\n\r\n"
        else:
            return -1

        server_address = (ip, port)
        server_socket.bind(server_address)

        while True:
            data, client_address = server_socket.recvfrom(1024)
            request = data.decode('utf-8')
            print(request)
            if request.startswith("GET"):
                server_socket.sendto(response_head.encode(), client_address)
                server_socket.close()
                return 1


def rudp_new_server(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        # SO_REUSEADDR is a socket option that allows the socket to be bound to an address that is already in use.
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Read contents of example.txt file
        with open('example.txt', 'r') as file:
            response_body = file.read()
        if ip == "10.0.2.15":
            response_head = "HTTP/1.1 200 OK\r\nLocation: http://redirected_http_server.com/example.txt\r\n\r\n"
            response = response_head + response_body
        address = (ip, port)
        server_socket.bind(address)

        while True:
            data, client_address = server_socket.recvfrom(1024)
            request = data.decode('utf-8')
            print(request)
            if request.startswith("GET"):
                server_socket.sendto(response.encode(), client_address)
                server_socket.close()
                break


if __name__ == "__main__":

    # status = tcp_server("0.0.0.0", 80)
    # if status == 1:
    #     tcp_new_server("10.0.2.15", 80)
    # else:
    #     print("got incorrect request")
    status = rudp_server("0.0.0.0", 80)
    if status == 1:
        rudp_new_server("10.0.2.15", 80)
    else:
        print("got incorrect request")
