import configparser

class Configuration:
    def __init__(self, configFile):
        config = configparser.ConfigParser()
        config.read(configFile)

        self.ServerWebsocketPort = config['DEFAULT']['SERVER_WEBSOCKET_PORT']
        self.ClientUrl = config['DEFAULT']['CLIENT_URL']
        self.Mode = config['DEFAULT']['MODE']

        self.WaitForConnectionsPacingSec = int(config['DEFAULT']['WAIT_FOR_CONNECTIONS_PACING_SEC'])
        self.SecondsToSleepOnTradeForMock = float(config['DEFAULT']['SECONDS_TO_SLEEP_ON_TRADE_FOR_MOCK'])
        self.ImplementMock = config['DEFAULT']['IMPLEMENT_MOCK'] == "True"

