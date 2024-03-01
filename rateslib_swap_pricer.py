from rateslib import *
import pandas as pd




data = pd.DataFrame({
    "Term": ["1W", "2W", "3W", "1M", "2M", "3M", "4M", "5M", "6M", "7M", "8M", "9M", "10M", "11M", "12M", "18M", "2Y", "3Y", "4Y",],
    "Rate": [5.31331,
5.31605,
5.31914,
5.32550,
5.33450,
5.33210,
5.31400,
5.29720,
5.26965,
5.24085,
5.20960,
5.17442,
5.13455,
5.09820,
5.06145,
4.75360,
4.54160,
4.25820,
4.10060,],
})



data["Termination"] = [add_tenor(dt(2024, 2, 28), _, "F", "nyc") for _ in data["Term"]]

sofr = Curve(
    id="sofr",
    convention="Act360",
    calendar="nyc",
    modifier="MF",
    interpolation="log_linear",
    nodes={
        **{dt(2024, 2, 3): 1.0},  # <- this is today's DF,
        **{_: 1.0 for _ in data["Termination"]},
    }
)

sofr_args = dict(effective=dt(2024, 2, 27), spec="usd_irs", curves="sofr")

solver = Solver(
    curves=[sofr],
    instruments=[IRS(termination=_, **sofr_args) for _ in data["Termination"]],
    s=data["Rate"],
    instrument_labels=data["Term"],
    id="us_rates",
)


data["DF"] = [float(sofr[_]) for _ in data["Termination"]]

print(data)

irs = IRS(
    effective=dt(2024, 5, 23),
    termination=dt(2025, 8, 25),
    notional=-100e6,
    fixed_rate=5.3,
    curves="sofr",
    spec="usd_irs",
)

npv = irs.npv(solver=solver)
dv01 = irs.delta(solver=solver).sum()
swap_rate = irs.rate(solver=solver)
print(npv)
print(dv01)
print(swap_rate)