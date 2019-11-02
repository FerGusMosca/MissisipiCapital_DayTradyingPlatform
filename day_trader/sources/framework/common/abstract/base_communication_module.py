class BaseCommunicationModule:
    def __init__(self):

        self.InvokingModule = None
        self.Configuration = None
        self.ModuleConfigFile = None

    def DoLog(self, msg, message_type):
        """ Log every message from strategy and other modules

        Args:
            msg (String): Message to log.
            message_type (:obj:`Enum`): MessageType (DEBUG, INFO, WARNING, ..).
        """
        if self.InvokingModule is not None:
            self.InvokingModule.DoLog(msg, message_type)
        else:
            print(msg)
