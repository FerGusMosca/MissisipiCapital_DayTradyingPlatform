import configparser

class Configuration:
    def __init__(self, configFile):
        config = configparser.ConfigParser()
        config.read(configFile)

        self.ServerWebsocketPort = config['DEFAULT']['SERVER_WEBSOCKET_PORT']
        self.ClientUrl = config['DEFAULT']['CLIENT_URL']
        self.Mode = config['DEFAULT']['MODE']

        self.WaitForConnectionsPacingSec = int(config['DEFAULT']['WAIT_FOR_CONNECTIONS_PACING_SEC'])

