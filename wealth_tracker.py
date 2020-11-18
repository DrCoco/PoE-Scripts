# Author: Kiran Chandradevan
# This script was an attmept to create a tool which would track a players wealth.
# The scrip only progressed to the point of tracking currency and fragment items
import requests
import settings
from time import time
import pandas as pd

def stringify(numFloat):
    return str(round(numFloat,2))

def downloadData():
    dataDict = {}
    # dataDict["UniqueArmour"] = requests.get("https://poe.ninja/api/data/itemoverview/?league=L" + settings.league + "n&type=UniqueArmour").json()
    # dataDict["UniqueWeapon"] = requests.get("https://poe.ninja/api/data/itemoverview/?league=" + settings.league + "&type=UniqueWeapon").json()
    # dataDict["DivinationCard"] = requests.get("https://poe.ninja/api/data/itemoverview/?league=" + settings.league + "&type=DivinationCard").json()
    # dataDict["UniqueAccessory"] = requests.get("https://poe.ninja/api/data/itemoverview/?league=" + settings.league + "&type=UniqueAccessory").json()
    # dataDict["UniqueMap"] = requests.get("https://poe.ninja/api/data/itemoverview/?league=" + settings.league + "&type=UniqueMap").json()
    # dataDict["UniqueJewel"] = requests.get("https://poe.ninja/api/data/itemoverview/?league=" + settings.league + "&type=UniqueJewel").json()
    # dataDict["Prophecy"] = requests.get("https://poe.ninja/api/data/itemoverview/?league=" + settings.league + "&type=Prophecy").json()
    dataDict["Currency"] = requests.get("https://poe.ninja/api/data/currencyoverview/?league=" + settings.league + "&type=Currency").json()
    dataDict["Fragment"] = requests.get("https://poe.ninja/api/data/currencyoverview/?league=" + settings.league + "&type=Fragment").json()
    return dataDict

#! Start of script
start_time = time()

#! OPTIONS
accountName = 
realm = "pc"



priceData = downloadData()
url = "https://www.pathofexile.com/character-window/get-stash-items?accountName={}&realm={}&league={}&tabs=0&tabIndex=0&public=false".format(accountName,realm,settings.league)
cookies = {"POESESSID":""} # Enter POESESSID
response = requests.get(url, cookies=cookies).json()
numTabs = response["numTabs"]
print("{} tabs found".format(numTabs))

df = pd.DataFrame(columns=['Name', 'Quantity', 'Value', 'Total'])
numItem = 0
for item in response["items"]:
    name = item['typeLine']
    quantity = item['stackSize']
    value = 0
    total = 0

    found = False
    for ninjaType in priceData:
        if not found:
            for ninjaItem in priceData[ninjaType]["lines"]:
                if item['typeLine'] == ninjaItem['currencyTypeName'] and not found:
                    found = True
                    value = ninjaItem['receive']['value']

                    total = quantity * value

                    dataList = [name, quantity, round(value,2), round(total,2)]
                    df.loc[numItem] = dataList
                    numItem +=1
                elif item['typeLine'] == "Chaos Orb" and not found:
                    found = True
                    value = 1
                    total = quantity * value

                    dataList = [name, quantity, round(value,2), round(total,2)]
                    df.loc[numItem] = dataList
                    numItem +=1

    if not found: print("Not found: {}".format(item['typeLine']))

df.sort_values(by=['Total'], inplace=True, ascending=False)
print(df)
total_wealth = df.sum(axis=0, skipna=True, numeric_only=True)[1]
print("Estimated wealth: {}c".format(round(total_wealth,2)))

elapsed_time = time() - start_time
print("Seconds to execute: " + stringify(elapsed_time))