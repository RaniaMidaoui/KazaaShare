from pwn import *
import glob
import pandas as pd
import hashlib
import csv
import os
import sys
import socket
import pickle

#ouverture de l'index
csv_list = r"C:\Users\hp\Desktop\KRAYA\PROJET\KaZaA\Supernode\index.csv" 
index_fields = ['sha1_hash', 'ip_address']
df_index = pd.read_csv(csv_list, index_col=None, delimiter=",", usecols=index_fields)

#ouverture du fichier host contenant tous les noeuds fils
csv_hosts = r"C:\Users\hp\Desktop\KRAYA\PROJET\KaZaA\Supernode\hosts.csv"
host_fields = ['ip_address','os']
df_hosts = pd.read_csv(csv_hosts, index_col=None, delimiter=",", usecols=host_fields)

nodes = df_hosts.ip_address #extraire seulement les addresses IP des noeuds fils 

index_of_host = 0 #compteur pour les noeuds
path = ""

msg = "UPDATE"
names = []


for host in nodes:

    #copier les fichier du noued "host" de l'index dans un autre index pour le traitement independant de chaque noeud
    host_df_index = df_index
    i=0
    for ipadd in df_index.ip_address:
        if ipadd != host:
            host_df_index=host_df_index.drop(host_df_index.index[i])

    print(host)
    
    # Demander la liste des fichiers partages du noeuds
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host,9998))

    s.send(bytes(msg, 'utf-8'))

    recvd_data = s.recv(2048)
    names = pickle.loads(recvd_data)
    files = ''.join(names)
    
    s.send(bytes("EXIT", 'utf-8'))
    s.close()

    print("Updating index with node "+host+ " shared files...")

    if df_hosts.os[index_of_host] == 'windows' :
        path = 'C:\SharedRTFiles\*'
    else:
        path = "~/SharedRTFiles/*"
    print("Updating from path "+ path)

    #Mise a jour de l'index par les nouveaux fichiers
    hash_exist = 0

    files = files.split("\n")


    for filename in files:
        if filename != '':
            print(filename)
            hash_name = hashlib.sha1(filename.encode('utf-8')).hexdigest()
            for name in host_df_index.sha1_hash:
                if hash_name == name:
                    hash_exist = 1
            if hash_exist != 0:
                pass
            else:
                new_entry = hash_name+","+host+"\n"
                with open(csv_list, "a+") as f:
                    f.write(new_entry)
            hash_exist =0

    index_of_host += 1

print("DONE UPDATING")
