from sources.framework.common.interfaces.icommunication_module import ICommunicationModule
from sources.framework.common.abstract.base_communication_module import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.configuration.configuration import *
from sources.framework.common.logger.message_type import *
from sources.framework.common.enums.Actions import *
from sources.framework.common.dto.cm_state import *
from sources.framework.common.enums.fields.portfolio_positions_list_field import *
from sources.framework.common.enums.fields.portfolio_position_field import *
from sources.framework.common.enums.fields.summary_field import *
from sources.framework.common.enums.fields.summary_list_fields import *
from sources.framework.common.enums.fields.error_field import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.data_access_layer.websocket_server import *
import tornado
import threading
import asyncio


class WebSocketModule(BaseCommunicationModule, ICommunicationModule):
    def __init__(self):
        self.LockConnections = threading.Lock()
        self.Configuration = None
        self.WebsocketServer = None
        self.Connections = []


    #region Private Methods


    def DoLog(self,msg, type):
        self.InvokingModule.DoLog(msg,type)

    def LoadConfig(self):
        self.Configuration = Configuration(self.ModuleConfigFile)
        return True

    def CreateConnection(self,handler):
        try:
            self.LockConnections.acquire()
            self.Connections.append(handler)
        finally:
            self.LockConnections.release()

    def RemoveConnection(self,handler):
        try:
            self.LockConnections.acquire()
            self.Connections.remove(handler)
        finally:
            self.LockConnections.release()

    def OpenWebsocket(self):
        try:
            asyncio.set_event_loop(asyncio.new_event_loop())
            self.WebsocketServer = tornado.web.Application([(r"/", WSHandler,{'pInvokingModule': self}),])
            self.WebsocketServer.listen(self.Configuration.WebsocketPort)
            self.DoLog("Websocket commands successfully opened on port {}: ".format(self.Configuration.WebsocketPort) , MessageType.INFO)
            tornado.ioloop.IOLoop.instance().start()
        except Exception as e:
            self.DoLog("Critical error opening websocket @OpenWebsocket: " + str(e), MessageType.ERROR)


    #endregion

    #region Event Methods

    def ProcessError(self,wrapper):
        try:
            errMessage = wrapper.GetField(ErrorField.ErrorMessage)
            self.LockConnections.acquire()
            for conn in self.Connections:
                conn.PublishError(errMessage)

            return CMState.BuildSuccess(self)

        except Exception as e:
            self.DoLog("Exception @WebsocketModule.ProcessError:{}".format(str(e)), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)
        finally:
            if self.LockConnections.locked():
                self.LockConnections.release()

    def ProcessExecutionSummaryList(self,wrapper):
        try:
            success = wrapper.GetField(SummaryListFields.Status)
            self.LockConnections.acquire()
            if success:
                summaries = wrapper.GetField(SummaryListFields.Summaries)
                dayTradingPosId = wrapper.GetField(SummaryListFields.PositionId)

                for conn in self.Connections:
                    conn.PublishExecutionSummaries(summaries,dayTradingPosId)
            else:
                err = wrapper.GetField(SummaryFields.Error)
                for conn in self.Connections:
                    conn.PublishError(err)

            return CMState.BuildSuccess(self)

        except Exception as e:
            self.DoLog("Exception @WebsocketModule.ProcessExecutionSummaryList:{}".format(str(e)), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)
        finally:
            if self.LockConnections.locked():
                self.LockConnections.release()


    def ProcessExecutionSummary(self,wrapper):
        try:
            success = wrapper.GetField(SummaryFields.Status)
            self.LockConnections.acquire()
            if success:
                summary = wrapper.GetField(SummaryFields.Summary)
                dayTradingPosId  = wrapper.GetField(SummaryFields.PositionId)

                for conn in self.Connections:
                    conn.PublishExecutionSummary(summary,dayTradingPosId)
            else:
                err = wrapper.GetField(SummaryFields.Error)
                for conn in self.Connections:
                    conn.PublishError(err)

            return CMState.BuildSuccess(self)

        except Exception as e:
            self.DoLog("Exception @WebsocketModule.ProcessExecutionSummary:{}".format(str(e)), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)
        finally:
            if self.LockConnections.locked():
                self.LockConnections.release()

    def ProcessPortfolioPosition(self,wrapper):
        try:

            self.LockConnections.acquire()
            dayTradingPosition = wrapper.GetField(PortfolioPositionFields.PortfolioPosition)
            for conn in self.Connections:
                conn.PublishOpenPosition(dayTradingPosition)

            return CMState.BuildSuccess(self)

        except Exception as e:
            self.DoLog("Exception @WebsocketModule.ProcessPortfolioPosition:{}".format(str(e)), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)
        finally:
            if self.LockConnections.locked():
                self.LockConnections.release()

    def ProcessPortfolioPositions(self,wrapper):
        try:
            success = wrapper.GetField(PortfolioPositionListFields.Status)
            self.LockConnections.acquire()
            if success:
                dayTradingPositions = wrapper.GetField(PortfolioPositionListFields.PortfolioPositions)

                for conn in self.Connections:
                    conn.PublishOpenPositions(dayTradingPositions)
            else:
                err = wrapper.GetField(PortfolioPositionListFields.Error)
                for conn in self.Connections:
                    conn.PublishError(err)

            return CMState.BuildSuccess(self)

        except Exception as e:
            self.DoLog("Exception @WebsocketModule.ProcessPortfolioPositions:{}".format(str(e)), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)
        finally:
            if self.LockConnections.locked():
                self.LockConnections.release()


    #endregion

    #region ICommunicationModule methods

    def ProcessMessage(self, wrapper):
        try:
            if wrapper.GetAction() == Actions.ERROR:
                return self.ProcessError(wrapper)
            elif wrapper.GetAction() == Actions.PORTFOLIO_POSITIONS:
                return self.ProcessPortfolioPositions(wrapper)
            elif wrapper.GetAction() == Actions.PORTFOLIO_POSITION:
                return self.ProcessPortfolioPosition(wrapper)
            elif wrapper.GetAction() == Actions.EXECUTION_SUMMARIES_LIST:
                return self.ProcessExecutionSummaryList(wrapper)
            elif wrapper.GetAction() == Actions.EXECUTION_SUMMARY:
                return self.ProcessExecutionSummary(wrapper)
            else:
                raise Exception("ProcessMessage: Not prepared to process message {}".format(wrapper.GetAction()))
        except Exception as e:
            self.DoLog("Critical error @WebsocketModule.ProcessMessage: " + str(e), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)


    def ProcessOutgoing(self, wrapper):
        pass

    def ProcessIncoming(self, wrapper):
        try:
            if wrapper.GetAction() == Actions.PORTFOLIO_POSITIONS_REQUEST:
                return self.InvokingModule.ProcessMessage(wrapper)
            elif wrapper.GetAction() == Actions.PORTFOLIO_POSITION_TRADE_LIST_REQUEST:
                return self.InvokingModule.ProcessMessage(wrapper)
            elif wrapper.GetAction() == Actions.NEW_POSITION:
                return self.InvokingModule.ProcessMessage(wrapper)
            elif wrapper.GetAction() == Actions.CANCEL_ALL_POSITIONS:
                return self.InvokingModule.ProcessMessage(wrapper)
            elif wrapper.GetAction() == Actions.CANCEL_POSITION:
                return self.InvokingModule.ProcessMessage(wrapper)
            else:
                raise Exception("ProcessIncoming: Not prepared to process message {}".format(wrapper.GetAction()))
        except Exception as e:
            self.DoLog("Critical error @WebsocketModule.ProcessIncoming: " + str(e), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)

    def Initialize(self, pInvokingModule, pConfigFile):
        self.ModuleConfigFile = pConfigFile
        self.InvokingModule = pInvokingModule
        self.DoLog("WebSocketModule  Initializing", MessageType.INFO)

        if self.LoadConfig():



            threading.Thread(target=self.OpenWebsocket, args=()).start()

            self.DoLog("DayTrader Successfully initialized", MessageType.INFO)
            return CMState.BuildSuccess(self)

        else:
            msg = "Error initializing config file for WebSocketModule"
            self.DoLog(msg, MessageType.ERROR)
            return CMState.BuildFailure(self,errorMsg=msg)

    # endregion

