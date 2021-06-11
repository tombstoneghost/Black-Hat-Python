import win32con
import win32api
import win32security

import wmi
import sys
import os

def get_process_privileges(pid):
    try:
        # Handle to target process
        hproc = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION, False, pid)

        # Open main process token
        htok = win32security.OpenProcessToken(hproc, win32con.TOKEN_QUERY)

        # List of privileges enabled
        privs = win32security.GetTokenInformation(htok, win32security.TokenPrivileges)

        priv_list = ""

        for i in privs:
            # Check if privilege is enabled
            if i[1] ==  3:
                priv_list += "%s|" % win32security.LookupPrivilegeName(None, i[0])
    except:
        priv_list="N/A"

    return priv_list

def log_to_file(message):
    fd = open("process_monitor_log.csv", "ab")
    fd.write("%s\r\n" % message)
    fd.close()

    return

# Create a log file header
log_to_file("Time, User, Executable, CommandLine, PID, Parent PID, Privileges")

# Instantiate WMI Interface
c = wmi.WMI()

# Create Process Monitor
process_watcher = c.Win32_Process.watch_for("creation")

while True:
    try:
        new_process = process_watcher()

        proc_owner = new_process.GetOwner()
        proc_owner = "%s\\%s" % (proc_owner[0], proc_owner[2])
        create_date = new_process.CreationDate
        executable = new_process.ExecutablePath
        cmdline = new_process.CommandLine
        pid = new_process.ProcessId
        parent_pid = new_process.ParentProcessId

        privileges = get_process_privileges(pid)

        process_log_message = "%s,%s,%s,%s,%s,%s,%s" % (create_date, proc_owner, executable, cmdline, pid, parent_pid, privileges)

        print(process_log_message)

        log_to_file(process_log_message)

    except:
        pass