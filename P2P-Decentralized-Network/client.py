import socket
import pickle

class Client(object):
    """
    The client class provides the following functionality:
    1. Connects to a TCP server
    2. Send serialized data to the server by requests
    3. Retrieves and deserialize data from a TCP server
    """

    def __init__(self):
        """
        Class constractpr
        """
        # Creates the client socket
        # AF_INET refers to the address family ipv4.
        # The SOCK_STREAM means connection oriented TCP protocol.
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientid = 0

    def get_client_id(self):
        return self.clientid

    def connect(self, host="127.0.0.1", port=12000):
        """
        TODO: Connects to a server. Implements exception handler if connection is resetted.
	    Then retrieves the cliend id assigned from server, and sets
        :param host:
        :param port:
        :return: VOID
        """
        self.clientSocket.connect((host, port))
        #self.client.connect((host, port))
        while True: # client is put in listening mode to retrieve data from server.
            data = self.receive()
            if not data:
                break
            # do something with the data
        self.close()

    def send(self, data):
        """
        TODO: Serializes and then sends data to server DONE
        :param data:
        :return:
        """
        data = pickle.dumps(data) # serialized data
        self.clientSocket.send(data)
        #self.client.send(data)


    def receive(self, MAX_BUFFER_SIZE=4090):
        """
        TODO: Desearializes the data received by the server DONE
        :param MAX_BUFFER_SIZE: Max allowed allocated memory for this data
        :return: the deserialized data.
        """
        raw_data = self.clientSocket.recv(MAX_BUFFER_SIZE) # deserializes the data from server
        #raw_data = self.client.recv(MAX_BUFFER_SIZE) # deserializes the data from server
        return pickle.loads(raw_data)

    def close(self):
        """
        TODO: close the client socket DONE
        :return: VOID
        """
        self.clientSocket.close()
        #self.client.close()



if __name__ == '__main__':
    client = Client()
    client.connect()
