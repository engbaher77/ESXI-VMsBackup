# VMsBackup-ESXI
Open Source Project to Schedule Backup VMs in Multiple ESXI Servers


# Features

### 1. Multiple ESXI Servers Backup

### 2. Entire VMS Backup for each Server

### 3. Backup scheduler

### 4. Exclude VMs from Backup



# Usage
All Configuration in config.ini file

### 1. Multiple ESXI Servers
```bash
[Servers]
host1 = 192.x.x.x
host2 = 192.x.x.x
```
### 2. Users Section Corresponding user for each host
```bash
[Users]
user1 = root
user2 = root
```
### 3. Passwords Section Corresponding password for each host
```bash
[PW]
password1 = ********
password2 = ********
```

### 4. Excluded VMS
```bash
[Excluded]
vm1 = Master
vm2 = BackEnd
```
