# Author: Kiran Chandradevan
# This is the first iteration of the recipe flipper
# Using recipes in the first iteration of manual recipes

import requests
import json
from time import sleep, time
import pandas as pd
import settings
from log_recipe import logger
start_time = time()
with open("test.json", 'r') as recipesFile:
    recipeSet = json.load(recipesFile)

def stringify(numFloat):
    return str(round(numFloat,2))

def downloadData():
    dataDict = {}
    dataDict["UniqueArmour"] = requests.get("https://poe.ninja/api/data/itemoverview/?league=" + settings.league + "&type=UniqueArmour").json()
    dataDict["UniqueWeapon"] = requests.get("https://poe.ninja/api/data/itemoverview/?league=" + settings.league + "&type=UniqueWeapon").json()
    dataDict["DivinationCard"] = requests.get("https://poe.ninja/api/data/itemoverview/?league=" + settings.league + "&type=DivinationCard").json()
    dataDict["UniqueAccessory"] = requests.get("https://poe.ninja/api/data/itemoverview/?league=" + settings.league + "&type=UniqueAccessory").json()
    dataDict["UniqueMap"] = requests.get("https://poe.ninja/api/data/itemoverview/?league=" + settings.league + "&type=UniqueMap").json()
    dataDict["UniqueJewel"] = requests.get("https://poe.ninja/api/data/itemoverview/?league=" + settings.league + "&type=UniqueJewel").json()
    dataDict["Prophecy"] = requests.get("https://poe.ninja/api/data/itemoverview/?league=" + settings.league + "&type=Prophecy").json()
    dataDict["Currency"] = requests.get("https://poe.ninja/api/data/currencyoverview/?league=" + settings.league + "&type=Currency").json()
    dataDict["Fragment"] = requests.get("https://poe.ninja/api/data/currencyoverview/?league=" + settings.league + "&type=Fragment").json()
    dataDict["Incubator"] = requests.get("https://poe.ninja/api/data/itemoverview/?league=" + settings.league + "&type=Incubator").json()
    dataDict["UniqueFlask"] = requests.get("https://poe.ninja/api/data/itemoverview/?league=" + settings.league + "&type=UniqueFlask").json()
    dataDict["SkillGem"] = requests.get("https://poe.ninja/api/data/itemoverview/?league=" + settings.league + "&type=SkillGem").json()
    dataDict["Oil"] = requests.get("https://poe.ninja/api/data/itemoverview/?league=" + settings.league + "&type=Oil").json()
    return dataDict

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

priceData = downloadData()
logger.info("Data download from poe.ninja API complete")

df = pd.DataFrame(columns=['Final Item','Profit Margin (%)','Profit (c)','Revenue (c)','Cost (c)', 'Num Listings'])
logger.info("DataFrame created")
numRecipes = len(recipeSet)
logger.info("Recipes found: " + stringify(numRecipes))
recipeCount = 0
profitableRecipes = 0
for recipe in recipeSet:
    logger.info("Recipe " + stringify(recipeCount+1) + " started")
    inputValue = 0
    outputValue = 0
    outputListings = 0

    for input in recipe['inputs']:
        logger.info(input)
        # ninjaURL = "https://poe.ninja/api/data/"
        # if input['type'] in ['Currency','Fragment']:
        #     ninjaURL += "currencyoverview"
        # else:
        #     ninjaURL += "itemoverview"
        # ninjaURL += "?league=Legion&"
        # ninjaURL += "type=" + input['type']
        # logger.info(ninjaURL)

        # ninjaResponse = requests.get(ninjaURL)
        # ninjaList = ninjaResponse.json()
        if input["type"] == 'Unknown':
            break
        else:
            ninjaList = priceData[input["type"]]

        found = False
        if input['type'] in ['Currency','Fragment']:
            for item in ninjaList['lines']:
                if item['currencyTypeName'] == input['name']:
                    inputValue += item['receive']['value'] * input['count']
                    logger.info("Found " + input['name'] + " at cost " + stringify(item['receive']['value']))
                    found = True
                    break
        else:
            for item in ninjaList['lines']:
                if item['name'] == input['name']:
                    if 'links' in input:
                        if item['links'] == input['links']:
                            inputValue += item['chaosValue'] * input['count']
                            logger.info("Found " + input['name'] + " at cost " + stringify(item['chaosValue']))
                            found = True
                            break
                    else:
                        inputValue += item['chaosValue'] * input['count']
                        logger.info("Found " + input['name'] + " at cost " + stringify(item['chaosValue']))
                        found = True
                        break
        if not found:
            print("Error occured, check logs")
            logger.error("Item not found: " + input['name'])
    logger.info("Input(s) value: " + stringify(inputValue))


    output = recipe['output']
    logger.info(output)
    # ninjaURL = "https://poe.ninja/api/data/"
    # if output['type'] in ['Currency','Fragment']:
    #     ninjaURL += "currencyoverview"
    # else:
    #     ninjaURL += "itemoverview"
    # ninjaURL += "?league=Legion&"
    # ninjaURL += "type=" + output['type']
    # logger.info(ninjaURL)

    # ninjaResponse = requests.get(ninjaURL)
    # ninjaList = ninjaResponse.json()
    if output["type"] == 'Unknown':
        recipeCount += 1
        printProgressBar(recipeCount,numRecipes,prefix='Data Analysis Progress',suffix='Complete',length=50)
        continue
    else:
        ninjaList = priceData[output["type"]]
    found = False
    if output['type'] in ['Currency', 'Fragment']:
        for item in ninjaList['lines']:
            if item['currencyTypeName'] == output['name']:
                outputValue += item['receive']['value'] * output['count']
                logger.info("Found " + output['name'] + " at cost " + stringify(item['receive']['value']))
                found = True
                break
    else:
        for item in ninjaList['lines']:
            if item['name'] == output['name']:
                if 'links' in output:
                    if item['links'] == output['links']:
                        outputValue += item['chaosValue'] * output['count']
                        outputListings= item['count']
                        logger.info(item['count'])
                        logger.info("Found " + output['name'] + " at cost " + stringify(item['chaosValue']))
                        found = True
                        break
                else:
                    outputValue += item['chaosValue'] * output['count']
                    outputListings = item['count']
                    logger.info(item['count'])
                    logger.info("Found " + output['name'] + " at cost " + stringify(item['chaosValue']))
                    found = True
                    break
    if not found:
        print("Error occured, check logs")
        logger.error("Item not found: " + output['name'])
    logger.info("Output(s) value: " + stringify(outputValue))

    profit = outputValue - inputValue
    profitMargin = profit*100/inputValue
    logger.info("Profit: " + stringify(profit))
    # if profit > 1: L Profits
    # if profit > 10 and profitMargin > 10: # M Profits
    # if profit > 30 and profitMargin > 10: # H Profits
    # if True: # All Recipes
    if profit > 10 and profitMargin > 10: # M Profits
        if "note" in recipe:
            dataList = [recipe['note'], int(profitMargin), int(profit), int(outputValue), int(inputValue),int(outputListings)]
        else:
            dataList = [recipe['output']['name'], int(profitMargin), int(profit), int(outputValue), int(inputValue), int(outputListings)]
        df.loc[recipeCount] = dataList
        profitableRecipes += 1
    recipeCount += 1
    printProgressBar(recipeCount,numRecipes,prefix='Data Analysis Progress',suffix='Complete',length=50)
    # print(stringify(profitMargin) + "%: " + recipe['output']['name'] + " makes " + stringify(profit) + "c, entry of " + stringify(inputValue) + "c")

print()
df.sort_values(by=['Profit Margin (%)'], inplace=True)
print(df)
elapsed_time = time() - start_time

print("Found {} recipes that met criteria out of {}".format(profitableRecipes, numRecipes))
print("Seconds to execute: {}".format(round(elapsed_time,2)))
print("Seconds per recipe: {}".format(round(elapsed_time/numRecipes,2)))