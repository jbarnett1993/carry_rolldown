from tia.bbg import LocalTerminal
import tia.bbg.datamgr as dm
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

mgr = dm.BbgDataManager()

# Dictionary of curves
curves = {
    'USD':'25','AUD': '1', 'CAD': '7', 'CHF': '82',
    'DEM': '16', 'GBP': '22', 'JPY': '18',
    'NZD': '49', 'SEK': '21', 'ITL': '40', 'BEF':'6',
    'FIM':'81', 'FRF':'14', 'GRD':'156','IEP': '62', 'NLG':'20',
    'PTE':'84', 'ESP':'61'
}

# Define start and end dates for the last week and last month
start_date = (datetime.today() - relativedelta(days=7)).strftime('%Y-%m-%d')
end_date = datetime.today().strftime('%Y-%m-%d')
start_last_month = (datetime.today() - relativedelta(months=1))
while start_last_month.weekday() >4:
    start_last_month -= timedelta(days=1)
start_last_month = start_last_month.strftime('%Y-%m-%d')
# Initialize lists for rolldowns
rolldowns = []
last_week_values = []
last_month_values = []

# Loop through each curve to fetch data
for ccy, curve in curves.items():
    curve_id = 'YCGT' + curve.zfill(4) + ' Index'
    resp = LocalTerminal.get_reference_data(curve_id, 'CURVE_TENOR_RATES')
    df = resp.as_frame()['CURVE_TENOR_RATES'][curve_id]
    tenors = df['Tenor']
    tenor_tickers = df['Tenor Ticker']
    mid_yield = df['Mid Yield']

    # Calculate the rolldown
    rolldown = np.diff(mid_yield).round(4)
    rolldown = np.insert(rolldown, 0, np.nan)  # Set first rolldown as NaN

    # Create a DataFrame with necessary information
    df_info = pd.DataFrame({
        'Currency': ccy,
        'Tenor': tenors,
        'Tenor Ticker': tenor_tickers,
        'yield': mid_yield,
        'Rolldown': rolldown
    })
    rolldowns.append(df_info)

# Concatenate rolldown DataFrames into a single DataFrame
rolldowns = pd.concat(rolldowns, ignore_index=True)
rolldowns.to_csv("all_curves.csv")

# Fetch historical data
rolldowns['sids'] = 'GT' + rolldowns['Currency'] + rolldowns['Tenor'] + ' Govt'
sids = mgr[rolldowns['sids'].to_list()]
last_week = sids.get_historical('YLD_YTM_MID', start_date, start_date).T
last_week.reset_index(inplace=True)
last_week.columns = ['sids', 'last_week_yield']

last_month = sids.get_historical('YLD_YTM_MID', start_last_month, start_last_month).T
last_month.reset_index(inplace=True)
last_month.columns = ['sids', 'last_month_yield']

tickers = mgr[rolldowns['Tenor Ticker'].to_list()]
countries = tickers.COUNTRY_FULL_NAME
countries.reset_index(inplace=True)
countries.columns = ['Tenor Ticker', 'Country']
# Merge the historical data with the rolldown DataFrame
combined_rolldowns = rolldowns.merge(last_week, on="sids")
combined_rolldowns = combined_rolldowns.merge(last_month, on="sids")
combined_rolldowns = combined_rolldowns.merge(countries, on="Tenor Ticker" )



# Add columns for last week and last month rolldown
combined_rolldowns['ccy_test'] = combined_rolldowns['Currency'].eq(combined_rolldowns['Currency'].shift())

combined_rolldowns['last_week_rolldown'] = np.where(
    combined_rolldowns['ccy_test'],
    combined_rolldowns['last_week_yield'] - combined_rolldowns.groupby('Currency')['last_week_yield'].shift(),
    np.nan
)

combined_rolldowns['last_month_rolldown'] = np.where(
    combined_rolldowns['ccy_test'],
    combined_rolldowns['last_month_yield'] - combined_rolldowns.groupby('Currency')['last_month_yield'].shift(),
    np.nan
)

# Save the combined DataFrame to CSV
combined_rolldowns.to_csv('combined_rolldowns_test.csv')

# Print the combined DataFrame
print(combined_rolldowns)



# Plotting each currency's yield curve with rolldown annotations on a separate page in a PDF
with PdfPages('sov_curve_rolldowns.pdf') as pdf:
    for country in combined_rolldowns['Country'].unique():
        fig, ax = plt.subplots(figsize=(10, 6))
        currency_data = combined_rolldowns[combined_rolldowns['Country'] == country]
        
        # Plot current yield and annotate rolldown
        ax.plot(currency_data['Tenor'], currency_data['yield'], marker='o', label='Current Yield')
        for i in range(len(currency_data)):
            ax.annotate(f"{currency_data.iloc[i]['Rolldown']:.2f}",
                        (currency_data.iloc[i]['Tenor'], currency_data.iloc[i]['yield']),
                        textcoords="offset points", xytext=(0,10), ha='center')

        # Plot last week's yield and annotate rolldown if available
        if 'last_week_yield' in currency_data.columns:
            ax.plot(currency_data['Tenor'], currency_data['last_week_yield'], marker='x', linestyle='--', label='Last Week Yield')
            for i in range(len(currency_data)):
                if pd.notnull(currency_data.iloc[i]['last_week_rolldown']):
                    ax.annotate(f"{currency_data.iloc[i]['last_week_rolldown']:.2f}",
                                (currency_data.iloc[i]['Tenor'], currency_data.iloc[i]['last_week_yield']),
                                textcoords="offset points", xytext=(0,-15), ha='center')

        # Plot last month's yield and annotate rolldown if available
        if 'last_month_yield' in currency_data.columns:
            ax.plot(currency_data['Tenor'], currency_data['last_month_yield'], marker='^', linestyle='--', label='Last Month Yield')
            for i in range(len(currency_data)):
                if pd.notnull(currency_data.iloc[i]['last_month_rolldown']):
                    ax.annotate(f"{currency_data.iloc[i]['last_month_rolldown']:.2f}",
                                (currency_data.iloc[i]['Tenor'], currency_data.iloc[i]['last_month_yield']),
                                textcoords="offset points", xytext=(0,-15), ha='center')

        # Formatting the plot
        ax.set_title(f'{country} Yield Curve')
        ax.set_xlabel('Tenor')
        ax.set_ylabel('Yield')
        ax.legend()
        ax.grid(True)
        
        # Save the current figure to its page
        pdf.savefig(fig)
        plt.close(fig)

