from client import Client
from server import Server
from tracker import Tracker
from config import Config
from downloader import Downloader
from threading import Thread
import uuid


class Peer(Server):
    """
    In this part of the peer class we implement methods to connect to multiple peers.
    Once the connection is created downloading data is done in similar way as in TCP assigment.
    """
    SERVER_PORT = 4999
    CLIENT_MIN_PORT_RANGE = 5001
    CLIENT_MAX_PORT_RANGE = 5010
    
    MAX_NUM_CONNECTIONS = 10
    MAX_UPLOAD_RATE = 100
    MAX_DOWNLOAD_RATE = 1000
    
    PEER = 'peer'
    LEECHER = 'leecher'
    SEEDER = 'seeder'

    def __init__(self, role=SEEDER, server_ip_address='127.0.0.1'):
        """
        Class constructor
        :param server_ip_address: used when need to use the ip assigned by LAN
        """
        Server.__init__(self, server_ip_address, self.SERVER_PORT)  # inherits methods from the server
        self.server_ip_address = server_ip_address
        self.id = uuid.uuid4()  # creates unique id for the peer
        self.role = role
        self.tracker = None
        
       

    def run_server(self):
        """
        Already implemented. puts this peer to listen for connections requests from other peers
        :return: VOID
        """
        try:
            # must thread the server, otherwise it will block the main thread
            server = Thread(target=self.run, daemon=False)
            server.start
            self.tracker = Tracker(server, "P2P-Project/P2P-Decentralized-Network/resources/age.torrent", self.id)
            self.setPeerTorrent(self.tracker.peer_id, self.tracker.torrent)
            self.tracker.run(self.tracker.peer_id)
        except Exception as error:
            print(error)  # server failed to run

    # noinspection PyMethodMayBeStatic
    def _connect_to_peer(self, client_port_to_bind, peer_ip_address, peer_port=5000):
        """
        This method connects a client from this peer to another peer.
        :param client_port_to_bind: port to bind the client to have more control over the ports used by our P2P network
        :param peer_ip_address: the ip address of the peer
        :param peer_port: the port of the peer
        :return: True if the client connected to the Peer. Otherwise, returns False
        """
        client = Client()
        try:
            # binds the client to the ip address assigned by LAN
            client.clientSocket.bind(('0.0.0.0', client_port_to_bind))  # note: when you bind, the port bound will be the client id
            Thread(target=client.connect, args=(peer_ip_address, peer_port)).start()  # threads server
            return True
        except Exception as error:
            print(error)  # client failed to bind or connect to server
            """
              Note that the following line does not unbind the port. Sometimes, once the socket is closed 
              The port will be still bound until WAIT_TIME gets completed. If you get the error: 
              "[Errno 48] Address already in use" 
              Then, go to your terminal and do the following to unbind the port:
                  lsof -i tcp:<client_port>
              Then copy the "pid" of the process, and execute the following
                  kill -i <pid>
              There are also other ways to unbind the port in code. Try the following line in the server file right 
              after you create the server socket
                  serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
              The above line only works sometimes depending on the system and how busy is your CPU.
            """
            client.close()
            return False

    def connect(self, peers_ip_addresses):
        """
        With this function this peer creates multiple clients that connect to multiple peers
        :param peers_ip_addresses: the ip addresses of the peers (their servers ip_addresses)
        :return: VOID
        """
        client_port = self.CLIENT_MIN_PORT_RANGE
        default_peer_port = self.SERVER_PORT
        for peer_ip in peers_ip_addresses:
            if client_port > self.CLIENT_MAX_PORT_RANGE:
                break
            if "/" in peer_ip:  # checks if the ip address includes ports
                # This part is good if your P2P supports sharing different files
                # Then the same peer can run different servers in the same machine
                ip_and_port = peer_ip.split("/")
                peer_ip = ip_and_port[0]  # the ip address of the peer
                default_peer_port = int(ip_and_port[1])  # the port of the peer
            if self._connect_to_peer(client_port, peer_ip, default_peer_port):
                # the client connected. incrementing the client port here prevents
                # wasting ports in the range of ports assigned if the client connection fails.
                client_port += 1


# testing
peer = Peer(role='peer')
print("Peer: " + str(peer.id) + " running its server: ")
peer.run_server()
#print("Peer: " + str(peer.id) + " running its clients: ")
# Two ways of testing this:
#  Locally (same machine):
#      1. Run two peers in the same machine using different ports. Comment out the next two lines (only servers run)
#      2. Then run a third peer, executing the next two lines of code.
#  Using different machines
#      1. Run two peers in different machines.
#      2. Run a peer in this machine.
#if peer.role == peer.LEECHER or peer.role == peer.PEER:
#    peer_ips = ['127.0.0.1/4999']  # this list will be sent by the tracker in your P2P assignment
#    peer.connect(peer_ips)

# 1st port 4999 this part commented out -> client from 2 success connected -> clientHandler error
# 2nd port 5000 with bottom code