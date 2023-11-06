
from tia.bbg import LocalTerminal
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np



curves = {
    'AUD': '1', 'CAD': '7', 'CHF': '82',
    'GER': '16', 'GBP': '22', 'JGB': '18',
    'nzd': '49', 'sek': '21', 'BTP': '40'
}

def get_curve(curves):
    pdf_pages = PdfPages('yield_curve_rolldown.pdf')

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
            'Tenor': tenors,
            'Tenor Ticker': tenor_tickers,
            'Mid Yield': mid_yield,
            'Rolldown': rolldown
        })
        
        # Exclude NaN values and sort dataframe by Rolldown (Descending)
        df_sorted = df_info.dropna().sort_values(by='Rolldown', ascending=False)

        # Extract top 3 with highest rolldown
        top_3 = df_sorted.head(3)

        fig, (ax_curve, ax_table) = plt.subplots(1, 2, figsize=(12, 6))

        ax_curve.plot(tenors, mid_yield, label=ccy)
        ax_curve.set_xlabel('Tenor')
        ax_curve.set_ylabel('Mid Yield')
        ax_curve.set_title(f'{ccy} Curve')
        ax_curve.legend()

        table_data = [
            ['Tenor', 'Tenor Ticker', 'Mid Yield', 'Rolldown'],
            *zip(top_3['Tenor'], top_3['Tenor Ticker'], top_3['Mid Yield'], top_3['Rolldown'])
        ]
        ax_table.axis('off')
        table = ax_table.table(cellText=table_data, loc='center')
        table.scale(1, 1.5)
        ax_table.set_title(f'Top 3 rolldown ({ccy})')

        plt.tight_layout()
        pdf_pages.savefig(fig, bbox_inches='tight')
        plt.close(fig)

    pdf_pages.close()


get_curve(curves)