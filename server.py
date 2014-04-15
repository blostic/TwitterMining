#!/usr/bin/python

from threading import Thread
from json_socket import JSONSocket, NoMessageAvailable
import time
import json

class Puppet(object):
    def __init__(self, socket, coordinates):
        self.socket = socket
        self.coordinates = coordinates

class Master(Thread):
    def __init__ (self, puppets):
        Thread.__init__(self)
        self.puppets = puppets
        self.overflow = False

    def check_if_alive():
        pass

    def merge_tweetless_area():
        pass

    def break_overflow_area():
        pass

    def run(self):
        while (True):
            for puppet in puppets:
                try:
                    msg = puppet.socket.recv()
                    print('recevied message:\n%s' % json.dumps(msg, indent = 4, separators = (',', ': ')))
                    #TODO: handle message
                except NoMessageAvailable:
                    pass

            time.sleep(1)

class Server(object):
    def __init__(self, puppets):
        self.puppets = puppets

    def get_coordinates(self):
        # na razie tylko zeby sprawdzic czy dziala, trzeba zrobic jakos "ladnie" to
        return [-180.0, -90.0, 180.0, 90.0]

    def start_server(self, hostname, port):
        print hostname

        thread = Master(self.puppets)
        thread.start()

        serverSocket = JSONSocket()
        serverSocket.bind((hostname, port))
        serverSocket.listen(5)
        while True:
            clientSocket, clientAddr = serverSocket.accept()
            coords = self.get_coordinates()
            self.puppets.append(
                Puppet(socket = clientSocket,
                       coordinates = coords)
            )

            print('connection from %s:%d' % clientAddr)
            clientSocket.send({
                'type': 'areaDefinition',
                'area': coords
            })

puppets  = []
Server(puppets).start_server('localhost', 12346)

