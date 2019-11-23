
class PositionStatisticalParameters():

    #region Constructors

    def __init__(self, tenMinSkipSlope, threeMinSkipSlope, threeToSixMinSkipSlope, threeToNineMinSkipSlope,
                      pctChangeLastThreeMinSlope,deltaCurrValueAndFiftyMMov):
        self.TenMinSkipSlope=tenMinSkipSlope
        self.ThreeMinSkipSlope=threeMinSkipSlope
        self.ThreeToSixMinSkipSlope=threeToSixMinSkipSlope
        self.ThreeToNineMinSkipSlope=threeToNineMinSkipSlope
        self.PctChangeLastThreeMinSlope=pctChangeLastThreeMinSlope
        self.DeltaCurrValueAndFiftyMMov=deltaCurrValueAndFiftyMMov