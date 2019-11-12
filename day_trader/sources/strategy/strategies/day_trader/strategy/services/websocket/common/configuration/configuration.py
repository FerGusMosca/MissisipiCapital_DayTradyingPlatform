import configparser

class Configuration:
    def __init__(self, configFile):
        config = configparser.ConfigParser()
        config.read(configFile)

        self.WebsocketPort = config['DEFAULT']['WEBSOCKET_PORT']
