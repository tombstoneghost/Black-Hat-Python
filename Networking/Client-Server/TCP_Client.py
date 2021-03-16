#!/bin/python3

import socket

target_host = "0.0.0.0"
target_port = 9999

# Create a Socket Object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the Client
client.connect((target_host, target_port))

# Sending Data
client.send("ABCEDF")

# Receiving Data
response = client.recv(4096)

print(response)
