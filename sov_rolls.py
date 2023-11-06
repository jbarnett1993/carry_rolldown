from tia.bbg import LocalTerminal
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from datetime import datetime, timedelta


curves = {
    'AUD': '1', 'CAD': '7', 'CHF': '82',
    'GER': '16', 'GBP': '22', 'JGB': '18',
    'nzd': '49', 'sek': '21', 'BTP': '40'
}

rolldowns = []
pdf_pages = PdfPages('yield_curve_rolldown.pdf')

# Previous date for yield curve
previous_date = datetime.now() - timedelta(days=7)

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
        'Rolldown': rolldown
    })

    rolldowns.append(df_info)

# Concatenate rolldown DataFrames into a single DataFrame
rolldowns = pd.concat(rolldowns, ignore_index=True)

# Save rolldown data to a CSV file
rolldowns.to_csv('rolldowns.csv', index=False)

for ccy, curve in curves.items():
    resp = LocalTerminal.get_reference_data('YCGT'+curve.zfill(4)+' Index','CURVE_TENOR_RATES')
    df = resp.as_frame()['CURVE_TENOR_RATES']['YCGT'+curve.zfill(4)+' Index']
    tenors = df['Tenor']
    tenor_tickers = df['Tenor Ticker']
    mid_yield = df['Mid Yield']
    
    # Retrieve previous yield curve data
    previous_resp = LocalTerminal.get_historical('YCGT'+curve.zfill(4)+' Index', 'CURVE_TENOR_RATES',
                                                 previous_date.strftime('%Y-%m-%d'), ignore_security_error=1)
    previous_df = previous_resp.as_frame()
    previous_mid_yield = previous_df[previous_date.strftime('%Y-%m-%d')]['Mid Yield']

    fig, (ax_curve, ax_table) = plt.subplots(1, 2, figsize=(12, 6))

    ax_curve.plot(tenors, mid_yield, label='Current')
    ax_curve.plot(tenors, previous_mid_yield, label='Previous')

    ax_curve.set_xlabel('Tenor')
    ax_curve.set_ylabel('Mid Yield')
    ax_curve.set_title(f'{ccy} Curve')
    ax_curve.legend()

    table_data = [
        ['Tenor', 'Tenor Ticker', 'Mid Yield'],
        *zip(tenors, tenor_tickers, mid_yield)
    ]
    ax_table.axis('off')
    table = ax_table.table(cellText=table_data, loc='center')
    table.scale(1, 1.5)
    ax_table.set_title(f'{ccy} Yield Curve Data')

    plt.tight_layout()
    pdf_pages.savefig(fig, bbox_inches='tight')
    plt.close(fig)

pdf_pages.close()