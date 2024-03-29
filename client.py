from sys import stdout
from time import sleep
from twython import TwythonStreamer
from json_socket import JSONSocket, NoMessageAvailable, ConnectionLost
from data_model import GenericTweet, EnglishTweet, dbConnect

import random
import json
import multiprocessing
import string
import time
import math
import traceback
import sys
import signal
import geohash

class TweetCounter:
    def __init__(self):
        self.downloadSpeed = 0.0
        self.lastCheckTime = time.time()
        self.tweetAddedQueue = multiprocessing.Queue()
        self.totalDownloaded = 0

    def count(self):
        now = time.time()

        tweetsDownloaded = 0
        while not self.tweetAddedQueue.empty():
            self.tweetAddedQueue.get()
            tweetsDownloaded += 1

        deltaTime = now - self.lastCheckTime
        self.downloadSpeed = float(tweetsDownloaded) / deltaTime
        self.lastCheckTime = now
        self.totalDownloaded += tweetsDownloaded

        global VERBOSE
        if VERBOSE:
            print('downloading %.4f tweets/s' % self.downloadSpeed)

class StreamerShutdown(Exception): pass


class Streamer(TwythonStreamer):
    def __init__(self, tweetAddedQueue, limitNoticeQueue, locations, *args, **kwargs):
        TwythonStreamer.__init__(self, *args, **kwargs)
        self.tweetAddedQueue = tweetAddedQueue
        self.limitNoticeQueue = limitNoticeQueue
        self.locations = locations

        self.statuses.filter(locations = self.locations)

    def on_success(self, data):
        if 'limit' in data:
            self.limitNoticeQueue.put(time.time())

        if 'geo' not in data:
            #print('not a tweet, skipping')
            #print(json.dumps(data, indent = 4, separators = (',', ': ')))
            return

        if data['geo'] is None:
            #print('error: no geolocation')
            return

        if 'lang' in data and data['lang'] == 'en':
            Streamer.save_english_tweet(data)
        Streamer.save_generic_tweet(data)

        self.tweetAddedQueue.put(1) # anything will do

    @staticmethod
    def save_english_tweet(data):
        tweet = Streamer.create_tweet(EnglishTweet, data)
        tweet.save()

    @staticmethod
    def create_tweet(constructor_method, data):
        hash = geohash.encode(data['geo']['coordinates'][0],data['geo']['coordinates'][1])
        geo = { 'lat': data['geo']['coordinates'][0], 'lon': data['geo']['coordinates'][1]}
        return constructor_method(
            tweetid=data['id'],
            userid=data['user']['id'],
            text=data['text'],
            in_reply_to_id=data['in_reply_to_status_id'],
            username=data['user']['name'],
            screen_name=data['user']['screen_name'],
            description=data['user']['description'],
            location=geo,
            geohash=hash
        )

    @staticmethod
    def save_generic_tweet(data):
        tweet = Streamer.create_tweet(GenericTweet, data)
        tweet.lang = data['lang'] if 'lang' in data else None
        tweet.save()

    def on_error(self, status_code, data):
        print('ERROR: %d' % status_code)
        print(data)

        if status_code == 420:
            print('420 error received, restarting after a 90 second wait period')

        self.disconnect()
        time.sleep(90)
        self.statuses.filter(locations = self.locations)


class StreamerSubprocess(object):
    def __init__(self, tweetAddedQueue, coordinates):
        self.limitNoticeQueue = multiprocessing.Queue()
        self.lastLimitNoticeTime = 0.0
        self.coordinates = coordinates
        self.process = multiprocessing.Process(target=spawnStreamer,
                                               args=([ tweetAddedQueue,
                                                       self.limitNoticeQueue,
                                                       coordinates ]))
        self.process.start()

    def updateLimitNoticeTime(self):
        while not self.limitNoticeQueue.empty():
            noticeTime = self.limitNoticeQueue.get()
            print(noticeTime - self.lastLimitNoticeTime)
            self.lastLimitNoticeTime = noticeTime

    def terminate(self):
        self.process.terminate()
        #TODO: graceful exit?

class Client(object):
    def handlePendingMessages(self):
        messages = {}
        while True:
            try:
                msg = self.socket.recv()
                msgType = msg['type']
                if msgType not in messages:
                    messages[msgType] = [ msg ]
                else:
                    messages[msgType].append(msg)
            except NoMessageAvailable:
                break

        # databaseAddress must be handled before areaDefinition
        for key in [ 'databaseAddress', 'areaDefinition' ]:
            if key in messages:
                msgs = messages[key]
                if len(msgs) > 1:
                    print('skipping %d old "%s" messages' % (len(msgs) - 1, key))
                self.handleMessage(msgs[-1])

    def handleMessage(self, msg):
        if msg['type'] == 'databaseAddress':
            self.setDatabase(msg['address'])
        elif msg['type'] == 'areaDefinition':
            self.resetStreamers(msg['area'])
        else:
            print('received message:\n%s' % json.dumps(msg, indent = 4, separators = (',', ': ')))

    def setDatabase(self, dbAddress):
        if self.databaseAddress != dbAddress:
            print('connecting to %s' % dbAddress)
            dbConnect(dbAddress)
            self.databaseAddress = dbAddress
        else:
            print('db address not changed (%s)' % self.databaseAddress)

    def initialized(self):
        return self.databaseAddress and self.coordinates

    def initialize(self):
        self.coordinates = None
        while not self.initialized():
            self.handlePendingMessages()

    def __init__(self, hostname, port):
        self.overflow = False;
        self.socket = JSONSocket()
        self.socket.connect((hostname, port))
        self.tweetCounter = TweetCounter()
        self.subprocesses = []
        self.coordinates = None
        self.databaseAddress = None

    def resetStreamers(self, coordinates):
        # TODO: podzielic jakos inteligentnie
        for subprocess in self.subprocesses:
            subprocess.terminate()
        self.subprocesses = []

        self.coordinates = coordinates
        print('gathering tweets from area: %s' % self.coordinates)
        for n in range(1):
            subprocess = StreamerSubprocess(self.tweetCounter.tweetAddedQueue,
                                            self.coordinates)
            self.subprocesses.append(subprocess)

    def run(self):
        try:
            self.initialize()

            while (True):
                # po zapytaniu servera czy zyjemy pasuje mu odpowiedziec ( i powiedziec czy mamy przepelnienei czy nie),
                # serwer moze nam powiedziec bysmy zmienili wspolrzedne po ktorych "szukamy"
                self.tweetCounter.count()
                self.socket.send({
                    'type': 'statusReport',
                    'downloadSpeed': self.tweetCounter.downloadSpeed
                })

                for subprocess in self.subprocesses:
                    subprocess.updateLimitNoticeTime()

                # TODO: jakis komunikat o osiagnieciu limitu, jesli twitter wysle takie info

                self.handlePendingMessages()
                time.sleep(1.0)
        finally:
            print('cleaning up subprocesses...')
            for subprocess in self.subprocesses:
                subprocess.terminate()

def spawnStreamer(tweetAddedQueue, limitNoticeQueue, vsp):
    global twitterKeys
    twitterKey = random.choice(twitterKeys)

    while True:
        try:
            stream = Streamer(tweetAddedQueue, limitNoticeQueue, vsp, *twitterKey)
        except StreamerShutdown:
            print('streamer shutting down')
            return
        except Exception as e:
            traceback.print_exc()
            print('error occurred, restarting streamer')

def sigusr1Handler(sigNum, stackFrame):
    global client
    counter = client.tweetCounter
    print >> sys.stderr, ('downloaded %d tweets, current speed: %.4f tweets/s'
                          % (counter.totalDownloaded, counter.downloadSpeed))

signal.signal(signal.SIGUSR1, sigusr1Handler)

AUTH_FILE = 'auth'
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12346

VERBOSE = False

if len(sys.argv) > 1 and sys.argv[1] == '-v':
    sys.argv.remove('-v')
    VERBOSE = True
    print('verbose mode on')

if len(sys.argv) not in [ 3, 4 ]:
    print('usage: client.py [ -v ] server_host server_port [ auth_file ]')
    sys.exit(1)

if len(sys.argv) == 4: AUTH_FILE = sys.argv[3]
if len(sys.argv) >= 3:
    SERVER_HOST = sys.argv[1]
    SERVER_PORT = int(sys.argv[2])

twitterKeys = [ x.strip().split(',') for x in open(AUTH_FILE).readlines() ]

client = Client(SERVER_HOST, SERVER_PORT)
client.run()

