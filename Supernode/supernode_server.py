import socket
import pandas as pd
import hashlib
from threading import Thread
from socketserver import ThreadingMixIn
import pickle
import glob
import time
import tqdm
import sys, os


separator = ","
host="192.168.57.47" #addresse du supernode

#ouverture de l'index
csv_list = r"C:\Users\hp\Desktop\KRAYA\PROJET\KaZaA\Supernode\index.csv"
index_fields = ['sha1_hash', 'ip_address']
df_index = pd.read_csv(csv_list, index_col=None, delimiter=",", usecols=index_fields)

#recherche du fichier dans l'index par son hash
def search_file(filename):
    dec_filename=filename.decode("utf-8")
    hash_name = hashlib.sha1(dec_filename.encode('utf-8')).hexdigest()
    index = 0 

    for name in df_index.sha1_hash:
        if hash_name == name:
            new_entry = df_index.ip_address[index]
            print(new_entry)
            with open("file_location.txt", "a+") as f:
                f.write(new_entry)
            index +=1


class myThread(Thread):
    def __init__(self,ip,port):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        print ("[+] Nouveau thread démarré pour " + ip + ":" + str(port))

    def run(self):

        os_type = sys.platform
        print(os_type)

        #inistialisation du path selon le systeme d'exploitation de l'ordinateur
        if (os_type == 'win32') or (os == 'win64') :
            path = 'C:\SharedRTFiles\*'
        else:
            path = "~/SharedRTFiles/*"

        while True :

            #attendre une requete
            request = con.recv(1024)
            print(request)

            #Traitement de la requete BROADCAST qui repond a un broadcast issu d'un autre supernode
            if request[:9] == bytes("BROADCAST",'utf-8'):
                broadcast_source = request[15:]
                print(broadcast_source)
                filename = con.recv(2048)
                dec_filename=filename.decode("utf-8")
                dec_filename= dec_filename[7:]

                #checher le fichier issu du broadcast dans les noeuds enfants du supernode et sauvegarder l'addresse I de celui qui a le fichier dans le fichier file_location.txt
                search_file(bytes(dec_filename, 'utf-8'))

                rep_req = "UPDATE_LOCATION"

                #envoyer une requete UPDATE_LOCATION au supernode qui a fait le broadcast pour qu'il lit les addresses IP qu'on vient de trouver (ceux dans file_location.txt)                
                con_update=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                con_update.connect((broadcast_source,9999))
                
                con_update.send(bytes(rep_req, 'utf-8'))
                time.sleep(1)
                
                file_location = open("file_location.txt","rb")
                
                for line in file_location:
                    if line != "":
                        con_update.send(line)
                        time.sleep(1)
                    else:
                        break                        
                
                file_location.close()   
                con_update.close()   
                
                open("file_location.txt","w").close()
                
                break
            
            # Traitement de la requete UPDATE_LOCATION issue d'un autre supernode apres l'envoie d'un broadcast, pour avoir les addresses ou se trouve le fichier
            if request == bytes("UPDATE_LOCATION",'utf-8'):

                time.sleep(3)
                while True:
                    new_line = con.recv(1024)
                    new_line= new_line.decode("utf-8")
                    if new_line=="":
                        break
                    with open("file_location.txt", "a+") as f:
                        f.write(new_line)
                break

            #Traitement de la requete SEARCH_SN issue d'un noued qui veut chercher quel noeuds contacter pour avoir un fichier donne
            if request == bytes("SEARCH_SN",'utf-8'):
    
                filename = con.recv(1024)
   
                #Verifier si l'un des noeuds fils a le fichier
                search_file(filename)
                
                req = "BROADCAST from "+host
                broadcast_message = b"Who has"+filename

                #Broadcast du nom du fichier our tous les autres supernodes du reseau 
                broadcast_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                broadcast_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                broadcast_soc.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

               
                broadcast_soc.bind((host, 10000))
                broadcast_soc.settimeout(0.2)

                broadcast_soc.sendto(bytes(req, 'utf-8'), ('<broadcast>', 10000))
                time.sleep(1)

                broadcast_soc.sendto(broadcast_message, ('<broadcast>', 10000))
                print("message sent!")
                time.sleep(1)

                broadcast_soc.close()

                #lire les addresses IP des noueuds contenat le fichier et les envoyer au noeud qui les a demande
                f=open("file_location.txt", "rb")
                for line in f:
                    if line!="":
                        con.send(line)
                        time.sleep(1)
                    else: 
                        break
                f.close()
                open("file_location.txt","w").close()

                break

        file_list = []

# Programme du serveur TCP
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, 9999))
mythreads = []

while True:
    s.listen(5)
    print("Serveur: en attente de connexions des clients TCP ...")
    (con, (ip,port)) = s.accept()
    mythread = myThread(ip,port)
    mythread.start()
    mythreads.append(mythread)

for t in mythreads:
    t.join()