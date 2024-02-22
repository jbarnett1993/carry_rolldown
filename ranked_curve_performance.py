from tia.bbg import LocalTerminal
import pandas as pd
import tia.bbg.datamgr as dm
from datetime import datetime
import numpy as np
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from tabulate import tabulate


# curves = {
#     'AUD': '1', 'CAD': '7', 'CHF': '82',
#     'GER': '16', 'GBP': '22', 'JGB': '18',
#     'nzd': '49', 'sek': '21', 'BTP': '40'
# }
mgr = dm.BbgDataManager()

start_date = (datetime.today() - relativedelta(years=1)).strftime('%Y-%m-%d')
end_date = datetime.today().strftime('%Y-%m-%d')

base_tickers = {
    'GER':'GTDEM', 'FRA':'GTFRF', 'ITA':'GTITL', 'ESP':'GTESP','UK':'GTGBP'
}

def get_historical_prices(ticker):
    return mgr.get_historical(ticker, ['PX_LAST'], start_date, end_date).iloc[:, 0]

df_2y = pd.DataFrame()
df_5y = pd.DataFrame()
df_10y = pd.DataFrame()
    
for country, base_ticker in base_tickers.items():
    df_2y[country+'_2y'] = get_historical_prices(base_ticker + '2Y Corp')
    df_5y[country+'_5y'] = get_historical_prices(base_ticker + '5Y Corp')
    df_10y[country+'_10y'] = get_historical_prices(base_ticker + '10Y Corp')

df_2y.fillna(method='ffill', inplace=True)

df_5y.fillna(method='ffill', inplace=True)

df_10y.fillna(method='ffill', inplace=True)


weekly_ret_2y = df_2y.iloc[-1] - df_2y.iloc[-6]
weekly_ret_5y = df_5y.iloc[-1] - df_5y.iloc[-6]
weekly_ret_10y = df_10y.iloc[-1] - df_10y.iloc[-6]

monthly_ret_2y = df_2y.iloc[-1] - df_2y.iloc[-21]
monthly_ret_5y = df_5y.iloc[-1] - df_5y.iloc[-21]
monthly_ret_10y = df_10y.iloc[-1] - df_10y.iloc[-21]

ranked_2y_weekly = weekly_ret_2y.sort_values()
ranked_5y_weekly = weekly_ret_5y.sort_values()
ranked_10y_weekly = weekly_ret_10y.sort_values()

ranked_2y_monthly = monthly_ret_2y.sort_values()
ranked_5y_monthly = monthly_ret_2y.sort_values()
ranked_10y_monthly = monthly_ret_2y.sort_values()


# Create a PDF document to save plots
pdf = PdfPages('yield_curve_charts.pdf')

# Define the dataframe, ranked returns, and titles
dataframes = [df_2y, df_5y, df_10y]
weekly_returns = [ranked_2y_weekly, ranked_5y_weekly, ranked_10y_weekly]
monthly_returns = [ranked_2y_monthly, ranked_5y_monthly, ranked_10y_monthly]
titles = ['2-Year Yield Curve', '5-Year Yield Curve', '10-Year Yield Curve']

# Iterate through the dataframes, weekly returns, and titles
for df, weekly_ret, monthly_ret, title in zip(dataframes, weekly_returns, monthly_returns, titles):
    # Create a new figure with subplots for the plot and table
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    # Plot the yield curve dataframe on the left-hand side subplot
    df.plot(ax=ax1)
    ax1.set_title(title)

    # Create the table with the weekly returns on the right-hand side subplot
    headers = ['Country', 'Weekly Return']
    table_data = list(zip(weekly_ret.index, np.round(weekly_ret.values, decimals=4)))
    ax2.table(cellText=table_data, colLabels=headers,
              cellLoc='center', loc='center')
    ax2.axis('off')

    # Set the layout of the subplots
    plt.tight_layout()

    # Save the figure to the PDF document
    pdf.savefig(fig)
    plt.close(fig)

# Close the PDF document
pdf.close()


# # Create a PDF document to save plots
# pdf = PdfPages('yield_curve_charts.pdf')

# # Plot df_2y and save to the PDF document
# plt.figure()
# df_2y.plot()
# plt.title('2-Year Yield Curve')
# pdf.savefig()
# plt.close()

# # Plot df_5y and save to the PDF document
# plt.figure()
# df_5y.plot()
# plt.title('5-Year Yield Curve')
# pdf.savefig()
# plt.close()

# # Plot df_10y and save to the PDF document
# plt.figure()
# df_10y.plot()
# plt.title('10-Year Yield Curve')
# pdf.savefig()
# plt.close()

# # Close the PDF document
# pdf.close()