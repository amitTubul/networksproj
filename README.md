
# Networks Project

This project demonstrates the implementation of a networking protocol that uses both TCP and a reliable version of UDP (RUDP), along with DHCP and DNS servers to manage client-server communication. 

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Dependencies](#dependencies)
- [Contributing](#contributing)
- [License](#license)

## Overview

This project explores network communication by setting up a client-server model that communicates using TCP or a custom Reliable UDP (RUDP) protocol. It includes a DHCP server to assign IPs and a DNS server to resolve domain names, creating a functional simulation of network-based interactions.

## Features

- **DHCP Server**: Assigns IP addresses to clients for network communication.
- **DNS Server**: Resolves domain names to IP addresses for the client.
- **HTTP Server**: Handles HTTP requests and provides a response.
- **RUDP Protocol**: Implements a UDP-based protocol with reliability features like SYN, FIN, and acknowledgment packets.
- **Error Handling**: Raises errors when encountering issues with packet loss or latency.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/amitTubul/networksproj.git
   ```

2. **Navigate to the project directory:**

   ```bash
   cd networksproj
   ```

3. **Install any necessary dependencies**:

   Ensure Python 3 is installed, and use the following command to install additional packages if required:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

To run the program, you’ll need four files: `client.py`, `dhcp.py`, `dns.py`, and `http_server.py`. Follow these steps to start the system:

1. Open separate terminals in the project directory for each file.

2. Run each script in the following order:

   ```bash
   sudo python3 dhcp.py
   sudo python3 dns.py
   sudo python3 http_server.py
   sudo python3 client.py
   ```

3. When prompted on the client terminal, choose between TCP or RUDP for communication.

### Process Overview

1. **DHCP Connection**: The DHCP server assigns an IP address to the client for communication with the DNS and HTTP servers.
2. **DNS Query**: The client sends a query to the DNS server, which responds with the HTTP server's address.
3. **Server Communication**: Depending on the chosen protocol (TCP or RUDP), the client establishes a connection with the HTTP server, sends a request, and receives a response.
4. **Redirection**: If necessary, the HTTP server may respond with a redirection, prompting the client to repeat the DNS and HTTP request process for the new address.

## Project Structure

- `client.py`: Manages client-side functionality, including connections with DHCP, DNS, and HTTP servers.
- `dhcp.py`: DHCP server that assigns IP addresses to clients.
- `dns.py`: DNS server for domain name resolution.
- `http_server.py`: Handles HTTP requests and responses.

## Dependencies

- `socket`: For creating and managing network connections.
- `threading`: To handle concurrent connections.
- `pcapng`: (If used) for capturing and analyzing packet exchanges.

## Error and Latency Handling

- **DHCP**: Raises an error if the client fails to obtain an IP address.
- **DNS**: Raises an error if an empty packet is received.
- **Application Layer**: TCP handles packet loss natively, while RUDP raises an error if no response is received after 5 seconds.

## Contributing

We welcome contributions! To contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -m 'Add feature'`).
4. Push to your branch (`git push origin feature-branch`).
5. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

---
