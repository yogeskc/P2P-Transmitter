from builtins import object
import socket
from threading import Thread
import pickle
from uploader import Uploader
#from client_handler import ClientHandler

class Server(object):

    MAX_NUM_CONN = 10

    def __init__(self, ip_address='127.0.0.1', port=12005):
        """
        Class constructor
        :param ip_address:
        :param port:
        """
        self.ip_address = ip_address
        self.port = port
        # create an INET, STREAMing socket
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {} # dictionary of clients handlers objects handling clients. format {clientid:client_handler_object}
        # TODO: bind the socket to a public host, and a well-known port DONE
        self.serversocket.bind((self.ip_address, self.port))
        self.peer_id = None
        self.torrent = None

    def setPeerTorrent(self, peer_id, torrent):
        self.peer_id = peer_id
        self.torrent = torrent

    def _listen(self):
        """
        Private method that puts the server in listening mode
        If successful, prints the string "Listening at <ip>/<port>"
        i.e "Listening at 127.0.0.1/10000"
        :return: VOID
        """
        #TODO: your code here DONE
        try:
            #self._bind()
            #self.serversocket.bind((self.ip_address, self.port))
            self.serversocket.listen(self.MAX_NUM_CONN)
            print("Server listening at ip/port", self.ip_address, self.port)
            # your code here
        except:
            self.serversocket.close()


    def _accept_clients(self):
        """
        Accept new clients
        :return: VOID
        """
        while True:
            try:
                #TODO: Accept a client DONE
                clientsocket, addr = self.serversocket.accept()
                #TODO: Create a thread of this client using the client_handler_threaded class DONE
                Thread(target=self.client_handler_thread, args=(clientsocket, addr)).start()  # client thread started
            except:
                #TODO: Handle exceptions DONE
                print("Could not connect to client")

    def send(self, clientsocket, data):
        """
        TODO: Serializes the data with pickle, and sends using the accepted client socket. DONE
        :param clientsocket:
        :param data:
        :return:
        """
        serialized_data = pickle.dumps(data)  # serialized data
        clientsocket.send(serialized_data)


    def receive(self, clientsocket, MAX_BUFFER_SIZE=4096):
        """
        TODO: Deserializes the data with pickle DONE
        :param clientsocket:
        :param MAX_BUFFER_SIZE:
        :return: the deserialized data
        """
        data_from_client = clientsocket.recv(MAX_BUFFER_SIZE)
        serialized_data = pickle.loads(data_from_client)  # deserializes the data from the client
        return serialized_data #change the return value after implemented.

    def send_client_id(self, clientsocket, id):
        """
        Already implemented for you
        :param clientsocket:
        :return:
        """
        clientid = {'clientid': id}
        self.send(clientsocket, clientid)

    def client_handler_thread(self, clientsocket, address):
        """
        Sends the client id assigned to this clientsocket and
        Creates a new ClientHandler object
        See also ClientHandler Class
        :param clientsocket:
        :param address:
        :return: a client handler object.
        """
        self.send_client_id(clientsocket, address[1])
        #TODO: create a new client handler object and return it DONE
        uploader = Uploader(self.peer_id, self, clientsocket, address, self.torrent)  # self is the server instance
        return uploader


    def run(self):
        """
        Already implemented for you. Runs this client
        :return: VOID
        """
        self._listen()
        self._accept_clients()


if __name__ == '__main__':
    server = Server()
    server.run()


