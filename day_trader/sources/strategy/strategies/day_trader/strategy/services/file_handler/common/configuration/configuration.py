import configparser

class Configuration:
    def __init__(self, configFile):
        config = configparser.ConfigParser()
        config.read(configFile)

        self.InputPath = config['DEFAULT']['INPUT_PATH']
        self.FailedPath = config['DEFAULT']['FAILED_PATH']
        self.ProcessedPath = config['DEFAULT']['PROCESSED_PATH']
