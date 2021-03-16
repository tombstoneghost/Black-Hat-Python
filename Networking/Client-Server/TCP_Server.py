#!/bin/python3

import socket
import threading

bind_ip = "0.0.0.0"
bind_port = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((bind_ip, bind_port))

server.listen(5)

print("[*] Listening on {ip}: {port}".format(ip=bind_ip, port=bind_port))


# Client Handling Thread
def handle_client(client_socket):
    # Printing what client is sending
    request = client_socket.recv(4096)
    print("[*] Received: ", request.decode())

    # Sending Back a Packet
    client_socket.send(b"ACK!")

    client_socket.close()


while True:
    client, addr = server.accept()

    print("[*] Accepted Connection from {ip}:{port}".format(ip=addr[0], port=addr[1]))

    # Client Thread to handle incoming data
    client_handler = threading.Thread(target=handle_client, args=(client,))
    client_handler.start()
