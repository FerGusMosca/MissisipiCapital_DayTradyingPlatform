from sources.framework.common.interfaces.icommunication_module import ICommunicationModule
from sources.framework.common.abstract.base_communication_module import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.configuration.configuration import *
from sources.framework.common.logger.message_type import *
from sources.framework.common.enums.Actions import *
from sources.framework.common.dto.cm_state import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.data_access_layer.websocket_server import *
import tornado
import threading

class WebSocketModule(BaseCommunicationModule, ICommunicationModule):
    def __init__(self):
        self.Configuration = None
        self.WebsocketServer = None

    def LoadConfig(self):
        self.Configuration = Configuration(self.ModuleConfigFile)
        return True

    def ProcessMessage(self, wrapper):
        try:
            if wrapper.GetAction() == Actions.ERROR:
                #TODO: publish errores
                return CMState.BuildSuccess(self)
            elif wrapper.GetAction() == Actions.PORTFOLIO_POSITION:
                #TODO: pulblish position status
                return CMState.BuildSuccess(self)
            else:
                raise Exception("ProcessMessage: Not prepared to process message {}".format(wrapper.GetAction()))
        except Exception as e:
            self.DoLog("Critical error @WebsocketModule.ProcessMessage: " + str(e), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)


    def ProcessOutgoing(self, wrapper):
        pass

    def OpenWebsocket(self):
        try:
            self.DoLog("Websocket commands successfully opened on port {}: ".format(self.Configuration.WebsocketPort) , MessageType.INFO)
            tornado.ioloop.IOLoop.instance().start()
        except Exception as e:
            self.DoLog("Critical error opening websocket @OpenWebsocket: " + str(e), MessageType.ERROR)


    def Initialize(self, pInvokingModule, pConfigFile):
        self.ModuleConfigFile = pConfigFile
        self.InvokingModule = pInvokingModule
        self.DoLog("WebSocketModule  Initializing", MessageType.INFO)

        if self.LoadConfig():

            self.WebsocketServer = tornado.web.Application([
                (r'/ws', WSHandler),
                (r'/', MainHandler),
                (r"/(.*)", tornado.web.StaticFileHandler, {"path": "./resources"}),
            ])
            self.WebsocketServer.listen(self.Configuration.WebsocketPort)

            threading.Thread(target=self.OpenWebsocket, args=()).start()

            self.DoLog("DayTrader Successfully initialized", MessageType.INFO)
            return CMState.BuildSuccess(self)

        else:
            msg = "Error initializing config file for WebSocketModule"
            self.DoLog(msg, MessageType.ERROR)
            return CMState.BuildFailure(self,errorMsg=msg)

