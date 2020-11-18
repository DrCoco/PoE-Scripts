# Author: Kiran Chandradevan
# This is the second iteration of the recipe flipper
# Using recipes in the second iteration of automated recipe generation

import requests
import json
from time import sleep, time
import pandas as pd
import settings
from log_recipe import logger

def fix_special_case(name):
    if name == 'Chaos Orb':
        return 1
    if 'Shard' in name:
        return 1
    if name == 'Scroll Fragment':
        return
    return 0

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

def stringify(numFloat):
    return str(round(numFloat,2))

def downloadData():
    dataDict = {}
    dataDict["Armour"] = requests.get("https://api.poe.watch/get?league=" + settings.league + "&category=armour").json()
    dataDict["Accessories"] = requests.get("https://api.poe.watch/get?league=" + settings.league + "&category=accessory").json()
    dataDict["Currency"] = requests.get("https://api.poe.watch/get?league=" + settings.league + "&category=currency").json()
    dataDict["Cards"] = requests.get("https://api.poe.watch/get?league=" + settings.league + "&category=card").json()
    dataDict["Flasks"] = requests.get("https://api.poe.watch/get?league=" + settings.league + "&category=flask").json()
    dataDict["Gems"] = requests.get("https://api.poe.watch/get?league=" + settings.league + "&category=gem").json()
    dataDict["Jewels"] = requests.get("https://api.poe.watch/get?league=" + settings.league + "&category=jewel").json()
    dataDict["Maps"] = requests.get("https://api.poe.watch/get?league=" + settings.league + "&category=map").json()
    dataDict["Prophecies"] = requests.get("https://api.poe.watch/get?league=" + settings.league + "&category=prophecy").json()
    dataDict["Weapons"] = requests.get("https://api.poe.watch/get?league=" + settings.league + "&category=weapon").json()
    dataDict["Beasts"] = requests.get("https://api.poe.watch/get?league=" + settings.league + "&category=beast").json()
    return dataDict

start_time = time()
with open("recipes.json", 'r') as recipesFile:
    recipeSet = json.load(recipesFile)

priceData = downloadData()

logger.info("Data download from poe.watch API complete")

df = pd.DataFrame(columns=['Final Item','Profit Margin (%)','Profit (c)','Revenue (c)','Cost (c)', 'Num Listings', "Main Component"])
logger.info("DataFrame created")
numRecipes = len(recipeSet)
logger.info("Recipes found: " + stringify(numRecipes))
recipeCount = 0
profitableRecipes = 0
for recipe in recipeSet:
    logger.info("Recipe " + stringify(recipeCount+1) + " started")
    inputValue = 0
    maxInputValue = 0
    outputValue = 0
    outputListings = 0
    mainComponent = ""

    # Skip Incursion Recipes Switch
    skip_incursion = True
    if skip_incursion:
        if len(recipe['inputs']) == 2 and 'Vial' in recipe['inputs'][1]['name']:
            continue

    for input in recipe['inputs']:
        logger.info(input)
        if input['type'] == 'Unknown':
            break
        else:
            categoryList = priceData[input["type"]]

        found = False
        for item in categoryList:
            if 'linkCount' in input:
                if item['name'] == input['name'] and item['linkCount'] == input['linkCount']:
                    inputValue += item['median'] * input['count']
                    inputListings = item['accepted']
                    logger.info(item['accepted'])
                    logger.info("Found " + input['name'] + " at cost " + stringify(item['median']))
                    found = True
                    break
            else:
                if item['name'] == input['name'] and 'linkCount' not in item:
                    inputValue += item['median'] * input['count']
                    inputListings = item['accepted']
                    logger.info(item['accepted'])
                    logger.info("Found " + input['name'] + " at cost " + stringify(item['median']))
                    found = True
                    break
        if not found:
            itemValue = fix_special_case(input['name'])
            inputValue += itemValue * input['count']
            inputListings = 0
            logger.info("Fixed " + input['name'] + " at cost " + stringify(itemValue))
            if itemValue == 0:
                print("Item not found (or fixed): " + input['name'])
                logger.error("Item not found (or fixed): " + input['name'])
        if item['median'] * input['count'] > maxInputValue:
            maxInputValue = item['median'] * input['count']
            mainComponent = str(input['count']) + "x " + input['name']
    logger.info("Input(s) value: " + stringify(inputValue))

    

    output = recipe['output']
    logger.info(output)
    if output["type"] == 'Unknown':
        recipeCount += 1
        continue
    else:
        categoryList = priceData[output["type"]]
    found = False
    for item in categoryList:
        if item['name'] == "Tabula Rasa" and output['name'] == "Tabula Rasa":
            logger.info("Name match: " + str(item))

        if 'gemLevel'in output and 'gemLevel' in item:
            if item['name'] == output['name'] and item['gemLevel'] == output['gemLevel']:
                outputValue += item['median'] * output['count']
                outputListings = item['accepted']
                logger.info(item['accepted'])
                logger.info("Found " + output['name'] + " at cost " + stringify(item['median']))
                found = True
                break

        elif 'linkCount' in output and 'linkCount' in item:
            if item['name'] == output['name'] and item['linkCount'] == output['linkCount']:
                outputValue += item['median'] * output['count']
                outputListings = item['accepted']
                logger.info(item['accepted'])
                logger.info("Found " + output['name'] + " at cost " + stringify(item['median']))
                found = True
                break
        elif item['name'] == output['name'] and 'linkCount' not in item and 'gemLevel' not in item and 'linkCount' not in output and 'gemLevel' not in output:
                outputValue += item['median'] * output['count']
                outputListings = item['accepted']
                logger.info(item['accepted'])
                logger.info("Found " + output['name'] + " at cost " + stringify(item['median']))
                found = True
                break
            
    if not found:
        itemValue = fix_special_case(output['name'])
        outputValue += itemValue * output['count']
        outputListings = 0
        logger.info("Fixed " + output['name'] + " at cost " + stringify(itemValue))
        if itemValue == 0:
            print("Item not found (or fixed): " + output['name'])
            logger.error("Item not found (or fixed): " + output['name'])
    logger.info("Output(s) value: " + stringify(outputValue))

    if outputValue != 0:
        profit = outputValue - inputValue
        profitMargin = profit*100/inputValue
        logger.info("Profit: " + stringify(profit))
        if profit > 0:
            profitableRecipes += 1
        dataList = [recipe['output']['name'], int(profitMargin), int(profit), int(outputValue), int(inputValue), int(outputListings), mainComponent]
        df.loc[recipeCount] = dataList
    recipeCount += 1
    printProgressBar(recipeCount,numRecipes,prefix='Data Analysis Progress',suffix='Complete',length=50)


print()
df.sort_values(by=['Profit Margin (%)'], inplace=True)
df.to_csv("recipeFlipper.csv", encoding='utf-8', index=False)
print(df[(df["Cost (c)"] < 10000) & (df["Profit (c)"] > 30)].tail(n=20))
elapsed_time = time() - start_time


print("Found {} recipes that met criteria out of {}".format(profitableRecipes, numRecipes))
print("Seconds to execute: {}".format(round(elapsed_time,2)))
print("Seconds per recipe: {}".format(round(elapsed_time/numRecipes,2)))

