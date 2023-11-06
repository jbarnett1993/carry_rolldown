import pandas as pd
import tia.bbg.datamgr as dm
import tia.analysis.ta as ta
import tia.analysis.model as model
from collections import OrderedDict

mgr = dm.BbgDataManager()


# Set the base ticker values for each currency
base_spot_tickers = {
    'aud': 'ADSW', 'cad': 'CDSW', 'chf': 'SFSNT',
    'eur': 'EUSA', 'gbp': 'BPSWS', 'jpy': 'JYSO',
    'nzd': 'NDSW', 'sek': 'SKSW', 'usd': 'USOSFR'
}

# Create an empty dictionary to hold the extended tickers
spot_curves = {}

# Specify the desired tenors
spot_tenors = list(range(1, 11)) + [15, 20]

# Extend the base tickers for each currency to include specified tenors
for currency, base_ticker in base_spot_tickers.items():
    spot_curves[currency] = [base_ticker + str(tenor) + ' Curncy' for tenor in spot_tenors]



spot_curves = pd.DataFrame.from_dict(spot_curves)

def replace_with_px_last(ticker):
    return mgr[ticker].PX_LAST

updated_spot_curves = spot_curves.applymap(replace_with_px_last)

print(updated_spot_curves)

# sids = mgr['ADSW1 Curncy', 'ADSW2 Curncy', 'ADSW3 Curncy', 'ADSW4 Curncy', 'ADSW5 Curncy', 'ADSW6 Curncy', 'ADSW7 Curncy', 'ADSW8 Curncy', 'ADSW9 Curncy', 'ADSW10 Curncy', 'ADSW15 Curncy', 'ADSW20 Curncy']

# prices = sids.PX_LAST



# # Create a DataFrame from the extended tickers dictionary
# spot_curves = pd.DataFrame.from_dict(spot_curves)

# # Flatten DataFrame to get a list of all tickers for Bloomberg request
# tickers_flat_list = spot_curves.values.flatten()

# # Request Bloomberg data for the tickers
# sids = mgr[tickers_flat_list]

# df_prices = sids.PX_LAST



# # # Pivot the resulting DataFrame to match the shape of the original spot_curves DataFrame
# # df_prices_pivot = df_prices.pivot_table(columns='ticker', values='PX_LAST')
# # df_prices_pivot.columns = df_prices_pivot.columns.remove_unused_levels().values  # clean up MultiIndex in columns

# print(df_prices)

# # # Reshape to the original DataFrame's structure, i.e., a column per each currency
# # price_curves = pd.DataFrame()
# # for currency in spot_curves.columns:
# #     currency_tickers = spot_curves[currency].values
# #     price_curves[currency] = df_prices_pivot[currency_tickers].values.flatten()

# # print(price_curves)





# # Add the 'tenor' column
# # spot_curves['tenor'] = [f"{i}y" for i in spot_tenors]

# # spot_curves.set_index('tenor', inplace=True)

# # # Set the 'tenor' column as the index
# spot_curves.set_index('tenor', inplace=True)



# base_fwd_tickers = {
#     'aud': 'SD0303FS', 'cad': 'SD4000FS', 'chf': 'S0234FS',
#     'eur': 'SD0045FS', 'gbp': 'S0141FS', 'jpy': 'S0195FS',
#     'nzd': 'SD0015FS', 'sek': 'SD0020FS', 'usd': 'S0490FS'
# }
