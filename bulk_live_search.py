# Author: Kiran Chandradevan
# Start with the bulk_item_prices.py script to select an item you want to buy
# The script will live search the bulk item exchange for new listings matching set conditions.
# A sound is played to alert the player of a new listing
# This method helps ignore any price fixing listings

import requests
import json
from time import sleep, strftime, gmtime
import settings


from log_bulk_live import logger
from playsound import playsound

itemsSet = [
            # {"have":"chaos", "want":"gilded-sulphite-scarab","minimum":3,"max-price":9,"accounts":[]},
            # {"have":"chaos", "want":"gilded-bestiary-scarab","minimum":3,"max-price":9,"accounts":[]},
            # {"have":"chaos", "want":"gilded-breach-scarab","minimum":3,"max-price":9,"accounts":[]},
            {"have":"chaos", "want":"cartographers-delirium-orb","minimum":5,"max-price":10,"accounts":[]}
            # {"have":"chaos", "want":"fertile-catalyst","minimum":10,"max-price":3,"accounts":[]},
            # {"have":"chaos", "want":"foreboding-delirium-orb","minimum":5,"max-price":8,"accounts":[]}
            # {"have":"chaos", "want":"fuse","minimum":500,"max-price":0.7,"accounts":[]},
            # {"have":"chaos", "want":"a-serveants-heart","minimum":500,"max-price":0.7,"accounts":[]}
            # {"have":"chaos", "want":"serrated-fossil","minimum":2,"max-price":20,"accounts":[]}
            # {"have":"chaos", "want":"immortal-resolve","minimum":1,"max-price":140,"accounts":[]},
            # {"have":"exalt", "want":"immortal-resolve","minimum":1,"max-price":1.2,"accounts":[]},
            # {"have":"chaos", "want":"the-gladiator","minimum":1,"max-price":10,"accounts":[]},
            # {"have":"chaos", "want":"buried-treasure","minimum":2,"max-price":5,"accounts":[]}
           ]

def stringify(numFloat):
    return str(round(numFloat,2))

while(True):
    for items in itemsSet:
        logger.info("Have: " + items['have'] + " Want: " + items['want'])
        try:
            # ! Create the request payload to find accounts matching requiremnts
            payloadString = "{\"exchange\":{\"status\":{\"option\":\"online\"},\"have\":[\"" + items['have'] + "\"],\"want\":[\""+ items['want'] +"\"],\"minimum\":"+ str(items['minimum']) +"}}"
            logger.info("payloadString: " + payloadString)
            payloadJSON = json.loads(payloadString)
            accountsResponse = requests.post('https://www.pathofexile.com/api/trade/exchange/' + settings.league,json=payloadJSON)
            accountsJSON = accountsResponse.json()
            logger.info("Response: " + json.dumps(accountsJSON))

            # ! Result sent back
            if 'error' in accountsJSON:
                logger.error(accountsJSON['error']['message'])
            listingsID = accountsJSON['id']
            logger.info("Listings ID: " + listingsID)
            numListings = accountsJSON['total']
            logger.info("Number of Listings: " + stringify(numListings))
            listingAccounts = accountsJSON['result'][:10] # Can make setting for how far down the listings to go

            listingsURL = "https://www.pathofexile.com/api/trade/fetch/"
            for listing in listingAccounts:
                listingsURL += listing + ","
            listingsURL = listingsURL[:-1]
            listingsURL += "?query=" + listingsID + "&exchange"
            logger.info("Pulling listings from: " + listingsURL)

            listingsResponse = requests.get(listingsURL)
            listingsJSON = listingsResponse.json()
            listingsList = listingsJSON['result']
            logger.info(json.dumps(listingsJSON))

            newListings = 0
            for listing in listingsList:
                accountID = listing['listing']['price']['item']['id']
                buyRatio = listing['listing']['price']['exchange']['amount']/listing['listing']['price']['item']['amount']
                logger.info(accountID + "(buyRatio): " + stringify(buyRatio))

                if buyRatio <= items['max-price'] and accountID not in items['accounts']:
                    listingDict = {}
                    listingDict['sell'] = listing['listing']['price']['item']['amount']
                    listingDict['buy'] = listing['listing']['price']['exchange']['amount']
                    listingDict['stock'] = listing['listing']['price']['item']['stock']
                    listingDict['sellName'] = listing['listing']['price']['exchange']['currency']
                    listingDict['buyName'] = listing['listing']['price']['item']['currency']
                    listingDict['buyRatio'] = listingDict['buy']/listingDict['sell']
                    listingDict['sellRatio'] = listingDict['sell']/listingDict['buy']
                    listingDict['sellerName'] = listing['listing']['account']['name']
                    listingDict['sellerIGN'] = listing['listing']['account']['lastCharacterName']
                    listingDict['id'] = listing['listing']['price']['item']['id']
                    items['accounts'].append(listingDict['id'])
                    print('{} {:15} {:20} | {:30} : Stock:{:5} Price:{:4}'.format(strftime("%H:%M:%S", gmtime()), listingDict['buyName'],listingDict['sellerName'],listingDict['sellerIGN'],stringify(listingDict['stock']),stringify(listingDict['buyRatio'])))
                    # print(strftime("%H:%M:%S", gmtime()) + ": NEW " + listingDict['buyName'] + " listing from: " + listingDict['sellerName'] + " | " + listingDict['sellerIGN'] + " | Stock:" + stringify(listingDict['stock']) + " | Price:" +  stringify(listingDict['buyRatio']))
                    playsound('smw_coin.wav', False)
                    newListings+=1
                    logger.info("Appended: " + json.dumps(listingDict))

            if newListings == 0:
                print(strftime("%H:%M:%S", gmtime()) + ": Nothing new found")
        except KeyError:
            print("Error with: " + " -> ".join(items))
            logger.error("Error with: " + " -> ".join(items))
    sleep(30)
