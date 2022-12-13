import socket, time

host = "192.168.42.47"
port = 10000
 
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
address = (host,port)
client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
client.bind(('', 10000))
while True:
    data= client.recv(1024)
    print(data)
    filename = client.recv(1024)
    print(filename)

    if data[:9] == bytes("BROADCAST",'utf-8'):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, 9999))
        s.send(data)
        time.sleep(1)
        s.send(filename)
        