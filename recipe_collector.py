# Author: Kiran Chandradevan
# This script was used to retrieve data on item recipes, e.g. prophecy, breach, divination cards, incursion, vendor recipes
# Only needs to be run once a league to retrieve new recipes
# Fixes need to be made for certain items (Can't remember why these were required *confused face*)
# Recipes are manually removed based on low-value, old, random rewards
# Output is placed into recipes.json

import requests
import json

def fix_item(recipeItem, additional = None):
    if recipeItem['name'] == 'Skin of the Loyal':
        recipeItem['linkCount'] = 6
    if recipeItem['name'] == 'Skin of the Lords':
        recipeItem['linkCount'] = 6
    if recipeItem['name'] == 'Tabula Rasa':
        recipeItem['linkCount'] = 6
    if additional != None:
        if recipeItem['name'] == 'Enlighten Support' and additional['input_item_name'] == 'The Enlightened':
            recipeItem['gemLevel'] = 3
        if recipeItem['name'] == 'Enlighten Support' and additional['input_item_name'] == 'Wealth and Power':
            recipeItem['gemLevel'] = 4
        if recipeItem['name'] == 'Enhance Support' and additional['input_item_name'] == 'The Artist':
            recipeItem['gemLevel'] = 4
        if recipeItem['name'] == 'Empower Support' and additional['input_item_name'] == "The Dragon's Heart":
            recipeItem['gemLevel'] = 4

def find_item_type(output,recipeItem, itemsGGG):
    if output:
        recipeItemName = recipeItem['output']
    else:
        recipeItemName = recipeItem['input_item_name']

    for label in itemsGGG['result']:
        for entries in label['entries']:
            if 'name' in entries and recipeItemName == entries['name']:
                return label['label']
            elif 'type' in entries and recipeItemName == entries['type']:
                return label['label']

    return "Unknown"

def write_json_file(recipeList):
    with open('recipes.json', 'w') as json_file:
        json_file.write(json.dumps(recipeList, indent=4))

def is_unwanted_recipe(recipe):
    blacklist_words = ["Mirror Arrow", "Blink Arrow", "Simulacrum", "Mirror of Kalandra", "Song of the Sirens", "Reefbane", "A Master Seeks Help", "Amulet", "Scroll of Wisdom", "Vaal Regalia", "Vaal Axe", "Talisman", "The Celestial Justicar", "Bone Helmet", "Book of Reform", "Shard of Fate", "Flask", "The Endurance", "The Golden Era", "The King's Blade", "Fishing Rod", "The Old Man", "The Rabid Rhoa", "The Twins", "Incubator", "Emperor of Purity", "Orb of Chance", "Void of the Elements", "The Celestial Stone", "The Spoiled Prince", "The Archmage's Right Hand", "Iron Ring", "The Sacrifice", "The Porcupine", "Prosperity", "Bowyer's Dream", "Rain of Arrows", "Imperial Legacy", "The Metalsmith's Gift", "Lightning Warp", "Sharktooth Arrow Quiver", "Star of Wraeclast", "Bitterdream", "The Goddess Scorned", "Grave Knowledge", "The Skeleton", "Orb of Alteration", "Block Chance Reduction Support"]

    if any(blacklist_word in recipe['output'] for blacklist_word in blacklist_words):
        return True

    if any(blacklist_word in recipe['input_item_name'] for blacklist_word in blacklist_words):
        return True

    return False

def is_random_recipe(recipe):
    blacklist_words = ["The Risk", "Glimmer of Hope", "The Penitent", "Council of Cats", "The Bargain", "More is Never Enough", "The Lion", "Merciless Armament", "Perfection", "The Mountain", "The Dark Mage", "The Road to Power", "The Lord of Celebration", "The Gambler", "The Body", "Stacked Deck", "The Chains that Bind", "The Dapper Prodigy","Destined to Crumble", "The Carrion Crow", "Time-Lost Relic", "Arrogance of the Vaal", "Jack in the Box", "The Admirer", "Mitts","Akil's Prophecy", "Alone in the Darkness", "Assassin's Favour", "Atziri's Arsenal","The Eye of the Dragon", "The Garish Power", "The Mercenary", "The Void", "The Wretched", "The Wolverine", "The Wolf", "The Web", "The Warlord", "The Devastator", "The Explorer", "The Fox", "The Flora's Gift", "Gemcutter's Promise", "Emperor's Luck", "Hubris", "Cartographer's Delight", "The Cataclysm", "The Inoculated", "Boundless Realms", "The Master Artisan", "The Tyrant", "The Jester", "Gift of the Gemling Queen", "Dialla's Subjugation", "The Surgeon", "The Summoner", "The Lover", "Blessing of God", "Struck by Lightning", "The Opulent", "The Lord in Black", "The Tower", "Blind Venture", "The Sigil", "The Warden", "Remnant of Corruption", "Three Voices", "Azyran's Reward", "The Trial", "Lost Worlds", "Two-Stone Ring", "The Gentleman", "The Undaunted", "The Valkyrie", "The Breach", "The Battle Born", "The Traitor", "Hunter's Resolve", "Boon of the First Ones", "The Bones", "The Messenger", "The Rite of Elements", "Volatile Power", "Heterochromia", "Lysah's Respite", "The Encroaching Darkness", "The Dreamer", "The Aesthete"]

    if recipe['input_item_name'] in blacklist_words:
        return True
    else:
        return False

def is_old_recipe(recipe):
    blacklist_words = ["The Awakening", "Betrayal", "War for the Atlas", "Atlas of Worlds", "Legion", "Ancient Rivalries IV", "The Anvil", "Birth of the Three", "The Price of Protection", " Net", "Charan's Sword", "The Goddess Bound"]

    if any(blacklist_word in recipe['output'] for blacklist_word in blacklist_words):
        return True

    if any(blacklist_word in recipe['input_item_name'] for blacklist_word in blacklist_words):
        return True

    return False

def is_mtx_recipe(recipe):
    if "Microtransaction" in recipe['input_item_id']:
        return True

    return False



def is_essence_corruption_recipe(recipe):
    if "Essence" in recipe['input_item_id'] and "1" in recipe['input_amount']:
        return True
    
    return False

def is_vaal_orb_corruption_recipe(recipe):
    if "Vaal Orb" in recipe['input_item_name'] and "1" in recipe['input_amount']:
        return True
    
    return False

recipeList = []
limit = 500
offset = 0

while limit == 500:
    url = """https://pathofexile.gamepedia.com/api.php?action=cargoquery&tables=upgraded_from_groups&fields=_pageName%3Doutput, amount%3Dinput_amount, group_id%3Dinput_group_id, item_name%3Dinput_item_name, set_id%3Dinput_set_id,item_id%3Dinput_item_id,notes%3Dnotes&limit={}&offset={}&format=json""".format(limit, offset)
    resp = requests.get(url).json()
    for recipe in resp["cargoquery"]:
        recipeList.append(recipe['title'])

    numResults = len(resp["cargoquery"])
    if numResults == limit:
        print("Received {} results".format(numResults))
        offset += limit
    else:
        print("Received {} results".format(numResults))
        limit = 0

numLines= 0

for recipeLine in recipeList[:]:
    numLines += 1
    if is_random_recipe(recipeLine):
        recipeList.remove(recipeLine)
        continue
    if is_old_recipe(recipeLine):
        recipeList.remove(recipeLine)
        continue
    if is_mtx_recipe(recipeLine):
        recipeList.remove(recipeLine)
        continue
    if is_essence_corruption_recipe(recipeLine):
        recipeList.remove(recipeLine)
        continue
    if is_vaal_orb_corruption_recipe(recipeLine):
        index = recipeList.index(recipeLine)
        recipeList.pop(index)
        recipeList.pop(index-1)
        continue
    if is_unwanted_recipe(recipeLine):
        recipeList.remove(recipeLine)

# for recipeLine in recipeList:
#     itemNum = recipeLine['input_group_id']
#     if itemNum == "1":
#         print("{} needs {}x {} | {}".format(recipeLine['output'], recipeLine['input_amount'], recipeLine['input_item_name'], recipeLine['input_item_id']))
#     else:
#         print("and {}x {} | {}".format(recipeLine['input_amount'], recipeLine['input_item_name'],recipeLine['input_item_id']))


itemsGGG = requests.get("https://www.pathofexile.com/api/trade/data/items").json()

inputsList = []
finalRecipeList = []
recipeDict = {"inputs":[],"output":{}}
for i in range(len(recipeList)):
    itemNum = recipeList[i]['input_group_id']
    outputDict = {}
    inputDict = {}
    if itemNum == "1":
        if len(inputsList) != 0:
            recipeDict['inputs'] = inputsList
            outputDict['name'] = recipeList[i-1]['output']
            outputDict['type'] = find_item_type(True, recipeList[i-1], itemsGGG)
            outputDict['count'] = 1
            fix_item(outputDict, recipeList[i-1])
            recipeDict['output'] = outputDict
            # print(recipeDict)
            finalRecipeList.append(recipeDict.copy())
            outputDict = {}
            inputsList = []

    inputDict['name'] = recipeList[i]['input_item_name']
    inputDict['type'] = find_item_type(False, recipeList[i], itemsGGG)
    inputDict['count'] = int(recipeList[i]['input_amount'])
    fix_item(inputDict)

    inputsList.append(inputDict)

# Adds custom recipes
with open('custom_recipes.json', 'r') as json_file:
        custom_recipe_set = json.load(json_file)
        for custom_recipe in custom_recipe_set:
            finalRecipeList.append(custom_recipe)

# print(finalRecipeList)
write_json_file(finalRecipeList)


print("NumLines Received: " + str(numLines))
print("Recipes created: " + str(len(finalRecipeList)))
