import pandas as pd
import csv

##### Code to remove duplicates

dom = 'domain-csvs/tourism'
df = pd.read_csv(f'master.csv')

df_unique = df.dropna(subset=['wikipedia_link'])
df_unique = df.drop_duplicates(subset=['wikipedia_link'], keep='first')


df_unique.to_csv(f'master.csv', index=False)

##### Code to concatenate and make master csv

# domains = ["culture", "demography", "history", "economy", "education", "tourism", "politics"]

# df = pd.read_csv(f'domain-csvs/geography.csv')
# for domain in domains:
#     df2 = pd.read_csv(f'domain-csvs/{domain}.csv')
#     df = pd.concat([df, df2], ignore_index = True)

# df.to_csv('master.csv', index = False)

