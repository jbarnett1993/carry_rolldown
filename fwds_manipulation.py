import pandas as pd

# Read the fwds data
# Read the fwds data
fwds = pd.read_csv("fwds.csv").set_index('point')

# Create a copy of the fwds DataFrame
fwds_copy = fwds.copy()

# Iterate over each row
for index, row in fwds.iterrows():
    t1 = row['t1']
    t2 = row['t2']

    # Check if t1 is greater than 1
    if t1 > 1:
        # Get the corresponding row where t1 and t2 are reduced by 1
        rolled_back_row = fwds[(fwds['t1'] == (t1 - 1)) & (fwds['t2'] == (t2 - 1))]
        
        # Perform the subtraction for each value in the copy dataframe
        for column in fwds.columns:
            if column not in ['t1', 't2']:
                rolled_back_value = rolled_back_row[column].values[0]
                fwds_copy.at[index, column] -= rolled_back_value

# Print the modified copy DataFrame
print(fwds_copy)


fwds_copy.to_csv("output.csv")

