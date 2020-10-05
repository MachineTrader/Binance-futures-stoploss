from binance_f.model.constant import *

# Getting user input
g_api_key = ""
g_secret_key = ""

# Time frame
time_frame: CandlestickInterval() = CandlestickInterval.MIN15  # input("Enter time frame in minutes(1m 3m 15m 1H 1D):")
margin_type: FuturesMarginType = FuturesMarginType.CROSSED

# Leverage
inp_lev: int = 50

# Risk
inp_risk: float = 5.0

# Sleep
sleep_seconds: int = 10

# TP
use_tp: bool = False
inp_tp: float = 3.0  # Take profit as multiplier of sl

# SL / Trail
use_trail: bool = False
short_factor = 0.5  # 0 for no shortening, 1 for a shortening equal to profit


