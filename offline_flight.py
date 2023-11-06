import pandas as pd
import numpy as np

df = pd.read_csv('rolldowns.csv')
df1 = pd.read_csv('df_t.csv')


df1.reset_index(drop=True, inplace=True)
df1.columns = ['Tenor Ticker','last_week_yield']
# df1['rolldown'] = df1['Yield'].diff()
''' need to account for different curves, currently will be taking rolldown for 30yc1 - 3m c2 when we are not in hte first country curve'''

print(df1)



df3 = df.merge(df1, on="Tenor Ticker")
df3['ccy_test'] = df['Currency'].eq(df['Currency'].shift())
print(df3)


df3['last_week_rolldown'] = np.where(df3['ccy_test'] == True, df3['last_week_yield'].diff(),np.nan)
print(df3)


df3.to_csv("week_comparison.csv")

'''if next currency not equal to this currency, Nan?'''
''''''