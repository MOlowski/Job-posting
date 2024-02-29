import pandas as pd
import requests
from bs4 import BeautifulSoup

df = pd.read_csv('LinkedinJobsDF.csv')
df_tmp = df
df_tmp1 = df_tmp.loc[df_tmp['med_sal']!=0]

## recalculate salary from daily, monthly and yearly
## to only yearly values

df1=df_tmp1.groupby('loc')['Co_Nm'].count().reset_index().sort_values(by='Co_Nm',ascending=False)

df_more_than_50_off = df1.loc[(df1['Co_Nm']>50)&(df1['loc']!='United States')]

locations = df_more_than_50_off['loc'].tolist()

df_tmp2 = df_tmp1.loc[df_tmp1['loc'].isin(locations)]

df_tmp2 = df_tmp2.loc[df_tmp2['py_prd']!='ONCE']

df_tmp2['med_sal_yearly'] = df_tmp2.apply(
    lambda row: row['med_sal']*2080 if row['py_prd']=='HOURLY' else row['med_sal']*52 if row['py_prd']=='WEEKLY' else row['med_sal']*12 if row['py_prd']=='MONTHLY' else row['med_sal'], axis=1
                                        )

df_tmp2['max_sal_yearly'] = df_tmp2.apply(
    lambda row: row['max_sal']*2080 if row['py_prd']=='HOURLY' else row['max_sal']*52 if row['py_prd']=='WEEKLY' else row['max_sal']*12 if row['py_prd']=='MONTHLY' else row['max_sal'], axis=1
                                        )

df_tmp2['min_sal_yearly'] = df_tmp2.apply(
    lambda row: row['min_sal']*2080 if row['py_prd']=='HOURLY' else row['min_sal']*52 if row['py_prd']=='WEEKLY' else row['min_sal']*12 if row['py_prd']=='MONTHLY' else row['min_sal'], axis=1
                                        )

## getting live dollar exchange rate by web scraping
## to recalculate salary to polish currency

url = 'https://www.bankier.pl/waluty/kursy-walut/nbp/USD'

response = requests.get(url)

if response.status_code == 200:

    soup = BeautifulSoup(response.content, "html.parser")

    element = soup.find("div", class_="profilLast")

    dollar_exchange_rate = element.text.strip()
else:
    print("Failed. Status code:", response.status_code)
    
dollar_exchange_rate = dollar_exchange_rate[0:4]
dollar_exchange_rate= float(dollar_exchange_rate.replace(",","."))

df_tmp2['max_sal'] = df_tmp2['max_sal_yearly'].apply(lambda x: round(x*dollar_exchange_rate))
df_tmp2['med_sal'] = df_tmp2['med_sal_yearly'].apply(lambda x: round(x*dollar_exchange_rate))
df_tmp2['min_sal'] = df_tmp2['min_sal_yearly'].apply(lambda x: round(x*dollar_exchange_rate))

proccesed_df = df_tmp2

proccesed_df.to_csv("processed_data.csv", index=False)