# Author: Kiran Chandradevan
# This script was never finished
# The intention was to be able to calculate the profit margins from leveling any gem from 1/0 to 20/0 and 1/20 to 20/20

import requests
import json
from time import sleep, time
import pandas as pd
import settings

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total:
        print()

gem_data = requests.get("https://api.poe.watch/get?league=" + settings.league + "&category=gem").json()
print("Received gem data from PoEWatch")

gem_20_20 = []
gem_01_20 = []
gem_20_00 = []
gem_01_00 = []

gem_count = 0
for gem in gem_data:
    if gem['gemLevel'] == 20 and gem['gemQuality'] == 20 and gem['gemIsCorrupted'] == False:
        gem_20_20.append(gem)
    if gem['gemLevel'] == 1 and gem['gemQuality'] == 20 and gem['gemIsCorrupted'] == False:
        gem_01_20.append(gem)
    if gem['gemLevel'] == 20 and gem['gemQuality'] == 0 and gem['gemIsCorrupted'] == False:
        gem_20_00.append(gem)
    if gem['gemLevel'] == 1 and gem['gemQuality'] == 0 and gem['gemIsCorrupted'] == False:
        gem_01_00.append(gem)
    gem_count += 1
    printProgressBar(gem_count,len(gem_data),prefix='Categorisation Progress',suffix='Complete',length=50)

# 20 Quality Flip
df = pd.DataFrame(columns=['Gem Name','Profit Margin (%)','Profit (c)','Revenue (c)','Cost (c)'])

gem_count = 0
gem20_count = 0
for gem20 in gem_20_20:
    if gem20['daily'] > 1500:
        for gem01 in gem_01_20:
            if gem20['name'] == gem01['name']:
                profit = gem20['median'] - gem01['median']
                profit_margin = profit*100 / gem01['median']
                df.loc[gem_count] = [(gem20['name'] + " 20/20"), int(profit_margin), int(profit), int(gem20['median']), int(gem01['median'])]
                gem_count += 1
                break
    gem20_count += 1
    printProgressBar(gem20_count,len(gem_20_20),prefix='Categorisation Progress',suffix='Complete',length=50)

gem00_count = 0
for gem20 in gem_20_00:
    if gem20['daily'] > 1500:
        for gem01 in gem_01_00:
            if gem20['name'] == gem01['name']:
                profit = gem20['median'] - gem01['median']
                profit_margin = profit*100 / gem01['median']
                df.loc[gem_count] = [(gem20['name'] + " 20/00"), int(profit_margin), int(profit), int(gem20['median']), int(gem01['median'])]
                gem_count += 1
                break
    gem00_count += 1
    printProgressBar(gem00_count,len(gem_20_00),prefix='Categorisation Progress',suffix='Complete',length=50)

df.sort_values(by=['Profit (c)'], inplace=True)
print(df.tail(n=20))


