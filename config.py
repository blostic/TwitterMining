try:
    from configparser import SafeConfigParser
except ImportError:
    from ConfigParser import SafeConfigParser

import getopt
import operator
import sys

class ServerConfig(object):
    def __init__(self):
        self.server_host = '0.0.0.0'
        self.server_port = 12345

        self.db_host = '127.0.0.1'
        self.db_port = 27017
        self.db_name = 'twitter'

        self.verbose = False

        self.whole_world_coords = [ -180.0, -90.0, 180.0, 90.0 ]

    def __str__(self):
        return '\n'.join('* %s = %s' % x for x in sorted(self.__dict__.items(), key=operator.itemgetter(0)))

    @staticmethod
    def printHelp():
        help = '\n'.join([
            "usage: server.py [ options ... ]",
            "",
            "available options:",
            "  -h, --help - display this message",
            "  -p, --port PORT - bind to local PORT (default: 12345)",
            "  -d, --db DB_ADDR - use DB_ADDR database. DB_ADDR must be in 'mongodb://HOST:PORT/DB_NAME' format",
            "  --db-host HOST - connect to database at HOST",
            "  --db-port PORT - connect to database at PORT",
            "  --db-name NAME - use database NAME",
            "  -f, --config FILE - read config from FILE",
            "  -v, --verbose - print additional info",
            "",
            "config file format:",
            "",
            "[db]",
            "host = <address>",
            "port = [ 0 ... 65535 ]",
            "name = <string>",
            "",
            "[server]",
            "host = <address>",
            "port = [ 0 ... 65535 ]",
            "min_lon = [ -180.0 ... 180.0 ]",
            "max_lon = [ -180.0 ... 180.0 ]",
            "min_lat = [ -90.0 ... 90.0 ]",
            "max_lat = [ -90.0 ... 90.0 ]",
            "",
            "[debug]",
            "verbose = on|off"
        ])
        print(help)

    @staticmethod
    def fromConfigFile(filename):
        print('loading config from file: %s' % filename)

        config = SafeConfigParser()
        config.read(filename)

        ret = ServerConfig()

        ret.server_host = config.get('server', 'host')
        ret.server_port = config.getint('server', 'port')
        ret.whole_world_coords = [ config.getfloat('server', 'min_lon'),
                                   config.getfloat('server', 'min_lat'),
                                   config.getfloat('server', 'max_lon'),
                                   config.getfloat('server', 'max_lat') ]

        ret.db_host = config.get('db', 'host')
        ret.db_port = config.getint('db', 'port')
        ret.db_name = config.get('db', 'name')

        ret.verbose = config.get('debug', 'verbose')

        return ret

    @staticmethod
    def fromArgs(argv):
        ret = ServerConfig()
        args_long = [ 'help', 'port', 'db', 'db-host', 'db-port', 'db-name', 'config', 'verbose' ]
        opts, args = getopt.getopt(argv, 'hp:d:f:v', args_long)

        for o, a in opts:
            if o in ('-p', '--port'):
                ret.server_port = int(a)
            elif o in ('-d', '--db'):
                if not a.startswith('mongodb://'):
                    raise ValueError
                hostport, name = a[10:].split('/')
                host, port = hostport.split(':')
                ret.db_host = host
                ret.db_port = port
                ret.db_name = name
            elif o == '--db-host':
                ret.db_host = a
            elif o == '--db-port':
                ret.db_port = int(a)
            elif o == '--db-name':
                ret.db_name = a
            elif o in ('-f', '--config'):
                return ServerConfig.fromConfigFile(a)
            elif o in ('-v', '--verbose'):
                ret.verbose = True
            elif o in ('-h', '--help'):
                ServerConfig.printHelp()
                sys.exit(0)
            else:
                print('unrecognized option: ' + o)
                sys.exit(1)

        if args:
            print('ignoring arguments: ' + ' '.join(args))
                
        return ret

