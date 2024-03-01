import QuantLib as ql
from tia.bbg import LocalTerminal
import tia.bbg.datamgr as dm
import numpy as np
import pandas as pd


yts = ql.RelinkableYieldTermStructureHandle()

# instruments = [
#     ('depo', '6M', 0.025),
#     ('swap', '1Y', 0.031),
#     ('swap', '2Y', 0.032),
#     ('swap', '3Y', 0.035)
# ]
'''

Ccy	Floating rate index	Fixed Yield Basis	Fixed Payment Freq	Float Yield Basis	Float Payment Freq
EUR	ESTR	Act/360	Annual	Act/360	Annual
EUR	6M EURIBOR	30/360	Annual	Act/360	Semi Annual
GBP	SONIA	Act/365 Fixed	Annual	Act/365 Fixed	Annual
USD	SOFR	Act/360	Annual	Act/360	Annual
CAD	CORRA	Act/365 Fixed	Semi-Annual	Act/365 Fixed	Semi-Annual
JPY	TONA	Act/365 Fixed	Annual	Act/365 Fixed	Annual
SEK	3M STIBOR	30/360	Annual	Act/360	Quarterly
NOK	6M NIBOR	30/360	Annual	Act/360	Semi-Annual
AUD	6M BBSW	Act/365 Fixed	Semi-Annual	Act/365 Fixed	Semi-Annual
NZD	3M BKBM	Act/365 Fixed	Semi-Annual	Act/365 Fixed	Quarterly

'''


curves = {
    'USD':'490'
}
curve_ids = []
for ccy, curve in curves.items():
    curve_id = 'YCSW' + curve.zfill(4) + ' Index'
    curve_ids.append(curve_id)
resp = LocalTerminal.get_reference_data(curve_id, 'CURVE_TENOR_RATES')
df = resp.as_frame()

print(df)
df.to_csv('usd discount curve.csv')
exit()
helpers = ql.RateHelperVector()
index = ql.Euribor6M(yts)
for instrument, tenor, rate in instruments:
    if instrument == 'depo':
        helpers.append( ql.DepositRateHelper(rate, index) )
    if instrument == 'fra':
        monthsToStart = ql.Period(tenor).length()
        helpers.append( ql.FraRateHelper(rate, monthsToStart, index) )
    if instrument == 'swap':
        swapIndex = ql.EuriborSwapIsdaFixA(ql.Period(tenor))
        helpers.append( ql.SwapRateHelper(rate, swapIndex))
curve = ql.PiecewiseLogCubicDiscount(2, ql.TARGET(), helpers, ql.Actual365Fixed())


yts.linkTo(curve)
engine = ql.DiscountingSwapEngine(yts)

tenor = ql.Period('2y')
fixedRate = 0.05
forwardStart = ql.Period("2D")

swap = ql.MakeVanillaSwap(tenor, index, fixedRate, forwardStart, Nominal=10e6, pricingEngine=engine)


fairRate = swap.fairRate()
npv = swap.NPV()

print(f"Fair swap rate: {fairRate:.3%}")
print(f"Swap NPV: {npv:,.3f}")