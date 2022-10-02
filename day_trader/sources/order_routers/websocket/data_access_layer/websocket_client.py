from websocket import create_connection


class WebsocketClient():
    def __init__(self,url):
        self.ws = create_connection(url)

    #region public Methods

    def DoReceive(self):
        return self.ws.recv()

    def DoSendAsync(self,msg):
        self.ws.send(msg.toJSON())

    def PublishError(self,err):
        self.ws.send(err)

    def IsConnected(self):
        return self.ws.connected

    def DoClose(self):
        return self.ws.close()



    #endregion
