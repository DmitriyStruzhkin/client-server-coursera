import socket
import time

class ClientError(Exception):
    pass

class Client:

    def __init__(self, host, port, timeout=None):
        self._host = host
        self._port = port
        self._check = dict()
        self._timeout = timeout

    def get(self, key):
        HOST, PORT = self._host, self._port
        data = 'get {}'.format(key)

        # Create a socket (SOCK_STREAM means a TCP socket)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            sock.connect((HOST, PORT))
            try:
                sock.sendall(bytes(data + '\n', "utf-8"))
            except socket.error:
                raise ClientError

            # Receive data from the server and shut down
            
            received = str(sock.recv(1024), "utf-8")
            new = received.strip("\n").split()
            try:
                for i in range(1, len(new), 3):
                    if new[i] not in self._check:
                        self._check[new[i]] = [(int(new[i+2]), float(new[i+1]))]
                    else:
                        self._check[new[i]] += [(int(new[i+2]), float(new[i+1]))]
            except (IndexError, ValueError):
                raise ClientError

        for key in self._check.keys():
            self._check[key] = sorted(self._check[key])          
        return self._check

        # print("Sent:     {}".format(data))
        # print("Received: {}".format(received))
        # print(key)
                
    def put(self, key, value, timestamp=None):
        HOST, PORT = self._host, self._port

        # Create a socket (SOCK_STREAM means a TCP socket)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            data = 'put {} {} {}'.format(key, value, timestamp)
            if timestamp is None:
                data = 'put {} {} {}'.format(key, value, int(time.time()))
            
            # Connect to server and send data
            sock.connect((HOST, PORT))
            try:
                sock.sendall(bytes(data + '\n', "utf-8"))
            except socket.error:
                raise ClientError

            # Receive data from the server and shut down
            received = str(sock.recv(1024), "utf-8")
            if not received:
                raise ClientError
            if received == "error\nwrong command\n\n":
                raise ClientError
            if received == "ok\n\n":
                pass
        return received



client1 = Client("127.0.0.1", 8888, timeout=5)
client2 = Client("127.0.0.1", 8888, timeout=5)
client1.put("k1", 0.25, timestamp=1)
client2.put("k1", 2.156, timestamp=2)
client1.put("k1", 0.35, timestamp=3)
client2.put("k2", 30, timestamp=4)
client1.put("k2", 40, timestamp=5)
client1.put("k2", 41, timestamp=5)
client1.get("k2")
client1.get("k1")
client1.get("k3")