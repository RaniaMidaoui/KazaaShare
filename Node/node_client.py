from pwn import *
import socket
import tqdm
import os, sys
import time

request = "SEARCH"
request_sn = "SEARCH_SN"
separator = ","

os_type = sys.platform
print(os_type)
if (os_type == 'win32') or (os == 'win64') :
    path = 'C:\SharedRTFiles\\'
else:
    path = "~/SharedRTFiles/"

filename = input("Enter the name of the file you're looking for: ")
ip_address = input("Where should i start looking, enter an IP address: ")
sn_ip_address = "192.168.57.47"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((ip_address,9998))

s.send(bytes(request, 'utf-8'))
time.sleep(1)
s.send(bytes(filename, 'utf-8'))

data = s.recv(1024)

if data == bytes("YES",'utf-8') :
    filesize = s.recv(2000)
    print(filesize)
    filesize = int(filesize)
    print(filesize)
    progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    newfile = path + "copy_" + filename
    with open(newfile, "wb") as f:
            bytes_read = s.recv(1000000000)
            #if not bytes_read:    
            #    break
            f.write(bytes_read)
            progress.update(len(bytes_read))
    s.close()
else :
    sn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sn.connect((sn_ip_address,9999))
    sn.send(bytes(request_sn, 'utf-8'))
    time.sleep(1)
    sn.send(bytes(filename, 'utf-8'))

    time.sleep(10)
    while True:
        new_line = sn.recv(1024)
        new_line= new_line.decode("utf-8")
        if new_line=="":
            break
        with open("location.txt", "a+") as f:
            f.write(new_line)
    
    print("Received file location...")
    sn.close()
    f = open("location.txt","r")

    data = f.read()
    number_of_characters = len(data)
    if number_of_characters == 0:
        print("FILE NOT FOFUND!!")
        exit(0)
	
    for download_ip_address in f:
        print(download_ip_address)
        download_soc=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        download_soc.connect((download_ip_address,9998))
        
        download_soc.send(bytes(request, 'utf-8'))
        time.sleep(1)
        download_soc.send(bytes(filename, 'utf-8'))
        download_soc.recv(2000)
        time.sleep(1)
        filesize = download_soc.recv(2000)
        print(filesize)
        filesize = int(filesize)
        print(filesize)
        progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        newfile = path + "copy_" + filename
        with open(newfile, "wb") as f:
            bytes_read = download_soc.recv(1000000000)
            f.write(bytes_read)
            progress.update(len(bytes_read))
        download_soc.close()
        break

    f.close()