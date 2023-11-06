from tia.bbg import LocalTerminal
import tia.bbg.datamgr as dm
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

mgr = dm.BbgDataManager()


curves = {
    'AUD': '1', 'CAD': '7', 'CHF': '82',
    'GER': '16', 'GBP': '22', 'JGB': '18',
    'nzd': '49', 'sek': '21', 'BTP': '40'
}

start_date = (datetime.today() - relativedelta(days=7)).strftime('%Y-%m-%d')
end_date = datetime.today().strftime('%Y-%m-%d')

rolldowns = []
for ccy, curve in curves.items():
    resp = LocalTerminal.get_reference_data('YCGT'+curve.zfill(4)+' Index','CURVE_TENOR_RATES')
    df = resp.as_frame()['CURVE_TENOR_RATES']['YCGT'+curve.zfill(4)+' Index']
    tenors = df['Tenor']
    tenor_tickers = df['Tenor Ticker']
    mid_yield = df['Mid Yield']

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
sids = mgr[rolldowns['Tenor Ticker'].to_list()]


last_week = sids.get_historical('YLD_YTM_MID', start_date, start_date).T

# last_week['Tenor Ticker'] = last_week.index
last_week.reset_index(inplace=True)
last_week.columns = ['Tenor Ticker','last_week_yield']

combined_rolldowns = rolldowns.merge(last_week, on="Tenor Ticker")
combined_rolldowns['ccy_test'] = combined_rolldowns['Currency'].eq(combined_rolldowns['Currency'].shift())
combined_rolldowns['last_week_rolldown'] = np.where(combined_rolldowns['ccy_test'] == True, combined_rolldowns['last_week_yield'].diff(),np.nan)

combined_rolldowns.to_csv('combined_rolldowns.csv')





























'''uncomment these rows when i want to generate the pdf and save the csv files down'''



# Save rolldown data to a CSV file
# rolldowns.to_csv('rolldowns.csv', index=False)
# pdf_pages = PdfPages('yield_curve_rolldown.pdf')
# for ccy, curve in curves.items():

#     resp = LocalTerminal.get_reference_data('YCGT'+curve.zfill(4)+' Index','CURVE_TENOR_RATES')
#     df = resp.as_frame()['CURVE_TENOR_RATES']['YCGT'+curve.zfill(4)+' Index']
#     tenors = df['Tenor']
#     tenor_tickers = df['Tenor Ticker']
#     mid_yield = df['Mid Yield']
    
#     rolldown = np.diff(mid_yield).round(4)
#     rolldown = np.insert(rolldown, 0, np.nan)  # Set first rolldown as NaN

#     # Create a DataFrame with necessary information
#     df_info = pd.DataFrame({
#         'Tenor': tenors,
#         'Tenor Ticker': tenor_tickers,
#         'Mid Yield': mid_yield,
#         'Rolldown': rolldown
#     })
    
#     # Exclude NaN values and sort dataframe by Rolldown (Descending)
#     df_sorted = df_info.dropna().sort_values(by='Rolldown', ascending=False)

#     # Extract top 3 with highest rolldown
#     top_5 = df_sorted.head(5)

#     fig, (ax_curve, ax_table) = plt.subplots(1, 2, figsize=(12, 6))

#     ax_curve.plot(tenors, mid_yield, label=ccy)
#     ax_curve.set_xlabel('Tenor')
#     ax_curve.set_ylabel('Mid Yield')
#     ax_curve.set_title(f'{ccy} Curve')
#     ax_curve.legend()

#     table_data = [
#         ['Tenor', 'Tenor Ticker', 'Mid Yield', 'Rolldown'],
#         *zip(top_5['Tenor'], top_5['Tenor Ticker'], top_5['Mid Yield'], top_5['Rolldown'])
#     ]
#     ax_table.axis('off')
#     table = ax_table.table(cellText=table_data, loc='center')
#     table.scale(1, 1.5)
#     ax_table.set_title(f'Top 3 rolldown ({ccy})')

#     plt.tight_layout()
#     pdf_pages.savefig(fig, bbox_inches='tight')
#     plt.close(fig)

# # pdf_pages.close()


