import os
import subprocess
import paramiko
import urllib.parse
import configparser
import time
from datetime import datetime

Servers = []
Users = []
PW = []
Excluded = []

t = 5


def header():
    print('\n\n')
    print("This software build for AiActive Techonolgies SAE,")
    print("Programmed By Baher Elnaggar \u00a92018")
    print('----------------------------------------\n\n')


# Read Config.ini
def configuration():
    config = configparser.ConfigParser()
    config.read("config.ini")

    # Read Sections
    section = config.sections()

    # Read Servers Section
    _Servers = section[0]
    _Servers = config.items(_Servers)
    for srv in _Servers:
        Servers.append(srv)

    # Read Users Section
    _Users = section[1]
    _Users = config.items(_Users)
    for usr in _Users:
        Users.append(usr)

    # Read PWs Section
    _PW = section[2]
    _PW = config.items(_PW)
    for pw in _PW:
        PW.append(pw)

    # Read Excluded Section
    _excluded = section[3]
    _excluded = config.items(_excluded)
    for key, value in _excluded:
        Excluded.append(value)

    # for name, value in Servers_IP:
    #     print ('  %s = %s' % (name, value))
    #     # host = value
    # print("the Host    " + value)
    # # print (value)
    # ssh_connect(host, user_name, password)
    # countdown(t)  # Calling sleep function


# Execute SSH Command
def ssh_command(_ssh, command):
    ssh.invoke_shell()
    stdin, stdout, stderr = _ssh.exec_command(command)

    _result = stdout.read()
    if _result == '':
        _result = stderr.read()

    # print(f'command {_result}')
    return _result


# SSH Connect
def ssh_connect(host, user, key):
    try:
        print(f'Connecting To  {host}....')
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=host, username=user, password=key)
        print('Done ...')
        return ssh

    except Exception as e:
        print('Connection Failed')
        return False
        # print(e)


# Export VM
def exportVM():

    # Shutdown VM
    result = ssh_command(ssh, f'vim-cmd vmsvc/power.off {_id}')

    if result == b'Powering off VM:\n':
        print(f'Powering Off "{_name}"')

        # Build Query
        exportQuery = buildQuery(name, pw, ip, _name, backupPath)

        # Export OVF of VM
        try:
            process = subprocess.Popen(
                exportQuery,
                stdout=subprocess.PIPE,
                universal_newlines=True
            )

            while True:
                output = process.stdout.readline()
                print(output.strip())
                # Do something else
                return_code = process.poll()
                if return_code is not None:
                    print('RETURN CODE', return_code)
                    # Process has finished, read rest of the output
                    for output in process.stdout.readlines():
                        print(output.strip())

                    break

        except Exception as err:
            print(f'Cannot Backup {_name} : {err}')

    # Poweron VM
    ssh_command(ssh, f'vim-cmd vmsvc/power.on {_id}')

    return


def takeSnapshot():
    return


# Get VMS
def getVms(string):
    _vms = []
    # Split by new line
    lines = string.splitlines()

    # Drop first item header
    del lines[0]

    for line in lines:
        # split by spaces ("     ")
        lineItems = line.split()

        vmData = (lineItems[0], lineItems[1])
        _vms.append(vmData)

    print(f'VMS Data {_vms}')
    return _vms


#  is Exported before func
def isExportedBefore():
    return


# Building Query
def buildQuery(username, userpw, vmip, vm, backupPath):
    # filter password
    userpw = urllib.parse.quote(userpw)
    _query = f"C:\Program Files\VMware\VMware OVF Tool\ovftool.exe vi:///{username}:{userpw}@{vmip}/{vm} {backupPath}"
    return _query


def countdown(t):
    while t:
        mins, secs = divmod(t, 60)
        timeformat = '{:02d}:{:02d}'.format(mins, secs)
        print(timeformat, end='\r')
        time.sleep(1)
        t -= 1
    print('\n\n------------------------------')


if __name__ == '__main__':
    header()

    configuration()

    # Loop over Servers
    for srv, user, password in zip(Servers, Users, PW):
        # Unpack Tuples
        host, ip = srv
        _user, name = user
        _password, pw = password
        print("-----------------------------------\n\n\n")

        # connect ssh
        ssh = ssh_connect(ip, name, pw)
        if not ssh:
            print('SSH Connection Failed, Check Esxi SSH Port..')
            continue

        # Execute Command
        result = ssh_command(ssh, 'vim-cmd vmsvc/getallvms')
        if result == b'':
            print(f'SSH Command Not Valid, {result}')
            continue

        # Refine Results
        vms = getVms(result)

        # loop through each vm
        for _id, _name in vms:

            _id = _id.decode(encoding="utf-8")
            _name = _name.decode(encoding="utf-8")

            # Check if Excluded
            if _name in Excluded:
                print(f'{_name} Excluded ..')
                continue

            # Export VM -> ESXI-Backup/<host>/<vm-name>/<date>/files
            today = datetime.today().strftime('%Y-%m-%d')
            backupPath = f'D:\\{host}\\{today}\\'
            os.makedirs(backupPath, exist_ok=True)

            # Backup vm
            exportVM()

