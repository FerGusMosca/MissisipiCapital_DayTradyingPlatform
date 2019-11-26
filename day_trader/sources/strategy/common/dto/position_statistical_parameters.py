
class PositionStatisticalParameters():

    #region Constructors

    def __init__(self, tenMinSkipSlope, threeMinSkipSlope, threeToSixMinSkipSlope, sixToNineMinSkipSlope,
                      pctChangeLastThreeMinSlope,deltaCurrValueAndFiftyMMov):
        self.TenMinSkipSlope=tenMinSkipSlope
        self.ThreeMinSkipSlope=threeMinSkipSlope
        self.ThreeToSixMinSkipSlope=threeToSixMinSkipSlope
        self.SixToNineMinSkipSlope=sixToNineMinSkipSlope
        self.PctChangeLastThreeMinSlope=pctChangeLastThreeMinSlope
        self.DeltaCurrValueAndFiftyMMov=deltaCurrValueAndFiftyMMov