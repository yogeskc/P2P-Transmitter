from server import Server
from torrent import Torrent
import socket
import bencodepy
import threading

class Tracker:
    def __init__(self, server, torrent, uuid, announce=True, dht_port=6000):
        self.DHT_PORT = dht_port
        self.server = server
        self.torrent = Torrent(torrent)
        self.torrent_info_hash = self._get_torrent_info_hash()
        self._is_announce = announce
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.udp_socket.bind(("", self.DHT_PORT))
        self.non_broadcast_socket = None
        self.peer_id = {"info_hash":self.torrent_info_hash, "node_id":uuid, "server_ip":self.server.ip_address, "server_port":self.server.port}
        self._DHT = {str(self.torrent_info_hash):{str(uuid): str(self.server.ip_address + "/" + self.server.port)}} #table of hashes 
        # {<hash_info_1> : [nodes]}
        #peer_ips = ['127.0.0.1/4998', '127.0.0.1/4999']
        #everyone has the torrent + hash, requesting original
        #self.run(self.peer_id)


    def _get_torrent_info_hash(self):
        """
        TODO: creates the torrent info hash (SHA1) from the info section in the torrent file
        :return:
        """
        sha1 = self.torrent.info_hash()
        return sha1  # returns the info hash

    def add_peer_to_swarm(self, peer_id, peer_ip, peer_port):
        """
        TODO: when a peers connects to the network adds this peer
              to the list of peers connected
        :param peer_id: hash_info, ip, port, uuid
        :param peer_ip:
        :param peer_port:
        :return:
        """
        """
        for all swarms in the DHT, compare peer_id[0] to the hash_info of that swarm
        if it matches, add the (peer_ip, peer_port) as a node
        """
        self._DHT[peer_id["info_hash"]][peer_id["node_id"]] = str(peer_ip  + "/" + peer_port)

    def remove_peer_from_swarm(self, peer_id):
        """
        TODO: removes a peer from the swarm when it disconnects from the network
              Note: this method needs to handle exceptions when the peer disconnected abruptly without
              notifying the network (i.e internet connection dropped...)
        :param peer_id: hash_info, ip, port, uuid
        :return:
        """
        """
        for all swarms in the DHT, compare peer_id[0] to the hash_info of that swarm
        if it matches, delete the node with peer_id[1] and peer.id[2] in it
        """
        self._DHT[peer_id["info_hash"]].pop(peer_id["node_id"])

    def broadcast(self, message, self_broadcast_enable=False):
        """
        TODO: broadcast the list of connected peers to all the peers in the network.
        :return:
        """
        try:
            encoded_message = self.encode(message)
            self.udp_socket.sendto(encoded_message, ("<broadcast>", self.DHT_PORT))
            print("Broadcasting.....")
        except socket.error as error:
            print(error)

        pass  # your code here
    
    def send_udp_message(self, message, ip, port):
        #you can communicate with any peer, same as response 
        try:
            self.non_broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            message = self.encode(message)
            self.non_broadcast_socket.sendto(message, (ip, port))
        except:
            print("Error UDP Message")

    def broadcast_listener(self):
        try:
            print("Listening at DHT PORT: ", self.DHT_PORT)
            while True:
                raw_data, sender_ip_and_port = self.udp_socket.recvfrom(4096)
                if raw_data:
                    data = self.decode(raw_data) # infohash of new peer
                    ip_sender = sender_ip_and_port[0]
                    port_sender = sender_ip_and_port[0]
                    if(data["disconnect"]):
                        self.remove_peer_from_swarm(data)
                    else:
                        #sends DHT to broadcaster
                        self.send_udp_message(self._DHT, ip_sender, port_sender)
                    #self._network.append()
                    #self.data = data
                    #self.data['nodeId'] = {ip_sender,port_sender}
                    #self.process_query()
                    print("data recieved by sender", data, ip_sender, port_sender)
                    #you have ip and port, you can create tcp connection if you like
        except:
            print("Error listening for Broadcast DHT PORT")

    def encode(self, message):
        """
        bencodes a message
        :param message: a dictionary representing the message
        :return: the bencoded message
        """
        return bencodepy.encode(message)

    def decode(self, bencoded_message):
        """
        Decodes a bencoded message
        :param bencoded_message: the bencoded message
        :return: the original message
        """
        return bencodepy.decode(bencoded_message)

    def set_total_uploaded(self, peer_id):
        """
        TODO: sets the total data uploaded so far by the peer passed as a parameter
        :param peer_id:
        :return: VOID
        """
        pass  # your code here

    def total_downloaded(self, peer_id):
        """
        TODO: sets the total data downloaded so far by the peer passed as a parameter
        :param peer_id:
        :return: VOID
        """
        pass  # your code here

    def validate_torrent_info_hash(self, peer_torrent_info_hash):
        """
        TODO: compare the info_hash generated by this peer with another info_hash sent by another peer
              this is done to make sure that both peers agree to share the same file.
        :param peer_torrent_info_hash: the info_hash from the info section of the torrent sent by other peer
        :return: True if the info_hashes are equal. Otherwise, returns false.
        """
        return peer_torrent_info_hash == self.torrent_info_hash

    def run(self, peer_id, start_with_broadcast = True):
        """
        TODO: This function is called from the peer.py to start this tracker
        :return: VOID
        """
        if self._is_announce == True:
            threading.Thread(target=self.broadcast_listener).start()
            if start_with_broadcast:
                message =  peer_id # [info_hash]self.torrent_info_hash
                self.broadcast(message, self_broadcast_enable=True)
        else:
            print("Error Tracker DHT Protocol")