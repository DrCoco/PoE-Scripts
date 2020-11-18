# Author: Kiran Chandradevan
# This script was built to calcualte the profit margins for 5/6 linking all armours via Jeweller's Touch and Fated Connections prophecy
# After 1-2 weeks in the league this method becomes very good for currency making
# The profits intended here are on the low end
# It is possible to make more since the price variance between well-rolled and average rolled items with no links is
# lower than after 5/6 linking
# E.g. Roll premium at 0 links is 3c but roll premium at 5 links is 80c 

import json
import requests
from operator import itemgetter
import settings

response = requests.get("https://poe.ninja/api/data/itemoverview?league=" + settings.league + "&type=UniqueArmour&language=en")
response.text
lines = json.loads(response.text)

#Setting up to get the list of item names
listOfNames = []
items = lines['lines']
listOfItemPrices = []

for item in items:
    if item['itemType'] == "Body Armour":
        if item['name'] in listOfNames:
            pass
        else:
            listOfNames.append(item['name'])
#print(listOfNames)


# With the list iterate over to find the price of each links
for name in listOfNames:
    dict = {'name': name, 'chaos6': 0, 'chaos5': 0, 'chaos0': 0}
    for item in items:
        if name == item['name']:
            if item['count'] >= 8:
                if item['links'] == 6:
                    dict['chaos6'] = item['chaosValue']
                elif item['links'] == 5:
                    dict['chaos5'] = item['chaosValue']
                elif item['links'] == 0:
                    dict['chaos0'] = item['chaosValue']
    listOfItemPrices.append(dict)
#print(listOfItemPrices)

#Set price of Jeweller's Touch
touch = 5

# Set the price of Fated Connections
fatedc = 300

#5 Link Profits
listOf50ProfitableItems = []
for itemPrices in listOfItemPrices:
    entry = itemPrices['chaos0'] + touch
    chaos50diff = itemPrices['chaos5'] - entry
    if chaos50diff > 0:
        dict = {'name': itemPrices['name'], 'chaos50diff': int(chaos50diff), 'entry_cost': int(itemPrices['chaos0'] + touch)}
        listOf50ProfitableItems.append(dict)

listOf50ProfitableItemsOrdered = sorted(listOf50ProfitableItems, key=itemgetter('chaos50diff'), reverse=True)[:10]

print("5 LINK PROFIT")
print("===============")
for profitableItem in listOf50ProfitableItemsOrdered:
    print(profitableItem['name'] + " makes " + str(profitableItem['chaos50diff']) + "c with entry of " + str(profitableItem['entry_cost']) + "c")

#6 Link Profits
listOf60ProfitableItems = []
for itemPrices in listOfItemPrices:
    entry = itemPrices['chaos0'] + fatedc
    chaos60diff = itemPrices['chaos6'] - entry
    if chaos60diff > 0:
        dict = {'name': itemPrices['name'], 'chaos60diff': int(chaos60diff), 'entry_cost': int(entry)}
        listOf60ProfitableItems.append(dict)

listOf60ProfitableItemsOrdered = sorted(listOf60ProfitableItems, key=itemgetter('chaos60diff'), reverse=True)[:10]

print()
print("6 LINK PROFIT")
print("===============")
for profitableItem in listOf60ProfitableItemsOrdered:
    print(profitableItem['name'] + " makes " + str(profitableItem['chaos60diff']) + "c with entry of " + str(profitableItem['entry_cost']) + "c")