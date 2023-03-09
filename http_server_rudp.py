import re
import socket


def server(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # SO_REUSEADDR is a socket option that allows the socket to be bound to an address that is already in use.
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        if ip == "0.0.0.0":
            response_head = "HTTP/1.1 302 Found\r\nLocation: http://redirected_http_server.com/example.txt\r\n\r\n"
            response = response_head

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
                client_socket.sendall(response.encode())
                client_socket.close()
                server_socket.close()
                return 1


def new_server(ip, port):
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


if __name__ == "__main__":
    status = server("0.0.0.0", 80)
    if status == 1:
        new_server("10.0.2.15", 80)
    else:
        print("got incorrect request")