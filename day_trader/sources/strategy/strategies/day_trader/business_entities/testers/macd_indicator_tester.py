import ta
from ta.trend import MACD
import pandas as pd
import math

class MACDIndicatorTester():

    def __init__(self, slow=26, fast=12, sign=9):
        self.Slow = slow
        self.Fast = fast
        self.Sign = sign
        self.MACD = None
        self.LastMACD = 0
        self.LastProcessedDateTime = None

        self.CalculateMacd()


    def GetPrices(self):
        # Original Example
        return [2978.43
                ,2979.39
                ,3000.93
                ,3009.57
                ,3007.26
                ,2997.94
                ,3005.69
                ,3006.73
                ,3006.79
                ,2991.62
                ,2991.77
                ,2966.84
                ,2984.87
                ,2977.62
                ,2961.79
                ,2976.73
                ,2940.25
                ,2887.61
                ,2910.63
                ,2952.01
                ,2938.79
                ,2893.06
                ,2919.4
                ,2938.13
                ,2970.27
                ,2966.15
                ,2995.68
                ,2989.86
                ,2997.95
                ,2986.2
                ,3006.72
                ,2995.99
                ,3004.51
                ,3010.29
                ,3022.55
                ,3039.42
                ,3036.89
                ,3046.77
                ,3037.56
                ,3066.91
                ,3078.27
                ,3074.62
                ,3076.78
                ,3085.18
                ,3093.08
                ,3087.01
                ,3091.84
                ,3094.04
                ,3096.63
                ,3120.46
                ,3122.03
                ,3120.18
                ,3108.46
                ,3103.54
                ,3110.29
                ,3133.64
                ,3140.52
                ,3153.63
                ,3140.98
                ,3113.87
                ,3093.2
                ,3112.76
                ,3117.43
                ,3145.91
                ,3135.96
                ,3132.52
                ,3141.62
                ,3168.58
                ,3168.8
                ,3191.41
                ,3192.52
                ,3191.14
                ,3205.37
                ,3221.22
                ,3224.01
                ,3223.38
                ,3239.91
                ,3240.02
                ,3221.29
                ,3230.78
                ,3257.85
                ,3234.85
                ,3246.28
                ,3237.18
                ,3253.05
                ,3274.7
                ,3265.35
                ,3288.13
                ,3283.15
                ,3289.36
                ,3316.81
                ,3329.62
                ,3320.79
                ,3321.75
                ,3325.54
                ,3295.47
                ,3243.63
                ,3276.24
                ,3273.4
                ,3283.59
                ,3225.52
                ,3248.92
                ,3297.63
                ,3334.69
                ,3345.78
                ,3327.71
                ,3352.09
                ,3357.75
                ,3379.45
                ,3373.94
                ,3380.16
                ,3370.29
                ,3386.15
                ,3373.23
                ,3337.75
                ,3225.89
                ,3128.21
                ,3116.39
                ,2978.76
                ,2954.22
                ,3090.23
                ,3003.37
                ,3130.11
                ,3024.06
                ,2972.37
                ,2746.56
                ,2882.23
                ,2741.38
                ,2480.64
                ,2711.02
                ,2386.13
                ,2529.19
                ,2398.10]


    def CalculateMacd(self):

        prices= self.GetPrices()

        df = pd.Series(prices, name="macd")

        self.MacdEntity = MACD(close=df, n_slow=self.Slow, n_fast=self.Fast, n_sign=self.Sign, fillna=0)

        self.MACD = self.MacdEntity.macd()
        self.MACDSignal = self.MacdEntity.macd_signal()


        print("Printing MACD")
        for data in self.MACD:
            if(not math.isnan(data)):
                print (data)

        print("Printing MACD Signal")
        for data in self.MACDSignal:
            if (not math.isnan(data)):
                print(data)

        print("Done")

