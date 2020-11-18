# Author: Kiran Chandradevan
# The level_areas.json is not completely
# This script was made to display what level you should be in each area during the campaign
# E.g. the character should hit level 8 before Brutus to use the next available support gem
# Level by area is based on RaizQT's levelling guide
# I made this to stop myself from overlevelling during the campaign


from tkinter import *
import time
import json
import requests
root = Tk()

def getCurrentChar(characterName):

    requestURL = "https://www.pathofexile.com/character-window/get-characters?accountName=&realm=pc" # Enter your account name
    cookies = {"POESESSID": ""} # Enter your POESESSID
    accountsResponse = requests.get(requestURL, cookies=cookies)
    accountsJSON = accountsResponse.json()

    for char in accountsJSON:
        if char['name'] == characterName:
            return char['level']

def getNextLevelArea(current_level):
    next_level = str(current_level +1)
    with open("level_areas.json", 'r') as levelAreasFile:
        levelAreasSet = json.load(levelAreasFile)
    for level_area_key, level_area_value in levelAreasSet.items():
        if next_level == level_area_key:
            area = level_area_value

    return area



current_level = '0'
current_level_text = Label(root, font=('times', 20, 'bold'), fg='white', bg='black')
current_level_text.pack(fill=BOTH, expand=1)
def tick():
    global current_level
    # get the current local time from the PC
    level_value = getCurrentChar("DrPascal")
    new_level = "\nCurrent Level: " + str(level_value)
    new_level += "\n"
    new_level += "Hit level {} in: {}\n".format(level_value+1, getNextLevelArea(level_value))
    # if time string has changed, update it
    if new_level != current_level:
        current_level = new_level
        current_level_text.config(text=new_level)
    # calls itself every 10000 milliseconds
    # to update the display as needed
    current_level_text.after(10000, tick)
tick()
root.mainloop()