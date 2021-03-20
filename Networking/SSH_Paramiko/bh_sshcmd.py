#!/bin/python3
import threading
import paramiko
import subprocess

def ssh_command(ip, user, passwd, command):
    client = paramiko.SSHClient()

    # Load Host Keys
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    client.connect(ip, username=user, password=passwd)

    ssh_session = client.get_transport().open_session()

    if ssh_session.active:
        ssh_session.exec_command(command)
        print(ssh_session.recv(1024))

    return

ssh_command('TARGET_IP', 'USERNAME', 'PASSWORD', 'id')
