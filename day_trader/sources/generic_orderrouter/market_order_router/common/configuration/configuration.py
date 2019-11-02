import configparser


class Configuration:
    def __init__(self, configFile):
        config = configparser.ConfigParser()
        config.read(configFile)

        self.OutgoingModule = config['DEFAULT']['OUTGOING_MODULE']
        self.OutgoingConfigFile = config['DEFAULT']['OUTGOING_CONFIG_FILE']
