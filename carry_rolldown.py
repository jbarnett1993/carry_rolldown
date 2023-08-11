import pandas as pd
import numpy as np
import tia.bbg.datamgr as dm
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Define function for calculating carry and rolldown
def calc_carry_rolldown(spot_rate, forward_rate, horizon_spot_rate):
    carry = horizon_spot_rate - forward_rate
    rolldown = forward_rate - spot_rate + horizon_spot_rate
    return carry, rolldown

mgr = dm.BbgDataManager()

start_date = (datetime.today() - relativedelta(years=17)).strftime('%Y-%m-%d')
end_date = datetime.today().strftime('%Y-%m-%d')

# Define list of European swap rates to retrieve
tenors = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "0101", "0202", "0303", "0404", "0505", "0606", "0707", "0808", "0909", "1010"]
euro_swap_rates = [f"EUSA{tenor} Curncy" for tenor in tenors]

# Define list of horizon dates in years
horizon_dates = [0.25, 0.5, 1]

# Get historical data for European swap rates
data = mgr.get_historical(euro_swap_rates, ['PX_LAST'], start_date, end_date)

# Pivot data to create a DataFrame with swap rates by tenor and date
swap_rates = data['PX_LAST'].unstack()

# Create a DataFrame to store carry and rolldown analysis
carry_rolldown = pd.DataFrame(index=horizon_dates, columns=tenors)

# Loop over each horizon date
for horizon_date in horizon_dates:
    horizon_spot_rate = swap_rates.loc[end_date, "EUSA" + str(horizon_date).replace(".", "") + " Curncy"]
    
    # Loop over each tenor
    for tenor in tenors:
        if len(tenor) == 1:
            ticker = "EUSA" + tenor + " Curncy"
            spot_rate = swap_rates.loc[end_date, ticker]
            forward_rate = swap_rates.loc[end_date, ticker] - swap_rates.loc[end_date, "EUSA" + str(horizon_date).replace(".", "") + " Curncy"]
        else:
            ticker = "EUSA" + tenor[:2] + tenor[-2:] + " Curncy"
            spot_rate = swap_rates.loc[end_date, ticker]
            forward_rate = swap_rates.loc[end_date, ticker] - swap_rates.loc[end_date, "EUSA" + tenor + " Curncy"]
        
        carry, rolldown = calc_carry_rolldown(spot_rate, forward_rate, horizon_spot_rate)
        
        carry_rolldown.loc[horizon_date, tenor] = (carry, rolldown)

# Print the carry and rolldown analysis for each horizon date and tenor
print(carry_rolldown)
