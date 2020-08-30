class TGIndicator():


    def __init__(self):
        self.Reset()

    # region Private Methods

    def Reset(self):
        self.K=None
        self.LastProcessedDateTime = None


    #endregion


    #region Public Methods

    def HasValidValue(self):
        return self.K is not None and  self.K !=0

    def Update (self,TG_INDICATOR_KK,TG_INDICATOR_KX,TG_INDICATOR_KY,maxMonetaryProfitCurrentTrade,
                TPSDStartOfTrade,longRuleEnalbedModelParam,shortRuleEnalbedModelParam ):

        if longRuleEnalbedModelParam.IntValue is None and shortRuleEnalbedModelParam.IntValue is None:
            self.K=None
            return

        if maxMonetaryProfitCurrentTrade is None or TPSDStartOfTrade is None or TPSDStartOfTrade==0:
            self.K = None
        else:
            if TG_INDICATOR_KK.FloatValue is None:
                raise Exception("Must specify value KK for TG indicator as its trading rule is enabled")

            if TG_INDICATOR_KX.FloatValue is None:
                raise Exception("Must specify value KX for TG indicator as its trading rule is enabled")

            if TG_INDICATOR_KY.FloatValue is None:
                raise Exception("Must specify value KY for TG indicator as its trading rule is enabled")

            KK= TG_INDICATOR_KK.FloatValue
            KX= TG_INDICATOR_KX.FloatValue
            KY= TG_INDICATOR_KY.FloatValue


            self.K = KK + ( KX * (((KY*maxMonetaryProfitCurrentTrade)/TPSDStartOfTrade) -KK ) )

            if self.K>1:
                self.K=1



    #endregion