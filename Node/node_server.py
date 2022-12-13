import socket
from threading import Thread
from socketserver import ThreadingMixIn
import pickle
import glob
import time
import tqdm
import sys, os


separator = ","

#Nom d'utilisateur
login = os.getlogin()

class myThread(Thread):
    def __init__(self,ip,port):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        print ("[+] Nouveau thread démarré pour " + ip + ":" + str(port))

    def run(self):


        file_list = []
        
        #Initialisation du type du systeme d'exploitation
        os_type = sys.platform
        print(os_type)
        
        if (os_type == 'win32') or (os == 'win64') :
            path = 'C:\SharedRTFiles\*'
        else:
            path = "/home/"+login+"/SharedRTFiles/*"
        
        while True :
            request = con.recv(1024)
            print(request)

            #Traitement de la requete update qui enverra les fichiers au supernode our qu'il puisse mettre a jour l'index
            if request == bytes("UPDATE",'utf-8'):
                files = glob.glob(path + "*")
                for file in files:
                    file_list += file[17:]+"\n"
                data=pickle.dumps(file_list)
                con.send(data)
                break
            file_list = ''

            # Traitement de la requete SEARCH issue d'un noeud souhaitant telecharger un fichier, le serveur le lui enverra si le noeud a vraiment le fichier sinon il enverra NO
            if request == bytes("SEARCH",'utf-8'):
                filename = con.recv(1024)
                files = glob.glob(path + "*")
                exist = 0
                for file_ in files:
                    if bytes(file_[17:],'utf-8') == filename:
                        exist = 1
                        con.send(b"YES")
                        time.sleep(1)
                        filesize = os.path.getsize(file_)
                        con.send(f"{filesize}".encode())
                        time.sleep(1)
                        progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
                        with open(file_, "rb") as f:
                            bytes_read = f.read(1000000000)
                            con.sendall(bytes_read)
                            progress.update(len(bytes_read))
                if exist == 0:
                    con.send(b"NO")
                break

        file_list = []

# Programme du serveur TCP
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('192.168.57.47', 9998))
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
