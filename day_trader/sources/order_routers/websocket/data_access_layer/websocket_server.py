import winsound

from sources.framework.common.logger.message_type import *
from sources.order_routers.websocket.common.wrappers.execution_report_wrapper import *
from sources.order_routers.websocket.common.wrappers.market_data_wrapper import *
from sources.order_routers.websocket.common.DTO.market_data.market_data_dto import *
from sources.order_routers.websocket.common.DTO.order_routing.execution_report_dto import *
from sources.order_routers.websocket.common.DTO.subscriptions.websocket_subscribe_message import *
from sources.order_routers.websocket.common.DTO.order_routing.route_order_req import *
import tornado.websocket
import json
import asyncio
import threading


class WSHandler(tornado.websocket.WebSocketHandler):
    # region Private Methods

    def DoLog(self, msg, type):
        if (self.InvokingModule is not None):
            self.InvokingModule.DoLog(msg, type)

    async def WriteMessage(self, obj):
        self.write_message(obj.toJSON())

    def DoSendAsync(self, obj):
        routine = self.WriteMessage(obj)
        asyncio.run(routine)

    def DoSendResponse(self, obj):
        self.write_message(obj.toJSON())

    # endregion

    # endregion IncomingMethods



    # endregion

    # region WS Handler Methods

    def check_origin(self, origin):
        return True

    def initialize(self, pInvokingModule):
        self.InvokingModule = pInvokingModule
        self.SubscribedServices = {}

    def open(self):

        # self.write_message("The server says: 'Hello'. Connection was accepted.")

        try:
            self.InvokingModule.CreateConnection(self)
            self.DoLog("Client succesfully connected ", MessageType.INFO)
        except Exception as e:
            self.DoLog("Critical error opening websocket @WSHandler: " + str(e), MessageType.ERROR)
        finally:
            pass

    def on_message(self, message):

        try:

           self.InvokingModule.ProcessWebsocketMessage(message)

        except Exception as e:
            msg = "<order_router> Critical error @on_message @WSHandler: " + str(e)
            self.DoLog(msg, MessageType.ERROR)
            # self.PublishError(msg)

    def on_close(self):
        try:
            self.InvokingModule.RemoveConnection(self)
            self.DoLog("Client succesfully disconnected ", MessageType.INFO)
        except Exception as e:
            self.DoLog("Critical error closing  websocket @WSHandler: " + str(e), MessageType.ERROR)
        finally:
            pass

    # endregion
