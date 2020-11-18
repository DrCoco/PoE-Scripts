# Author: Kiran Chandradevan
# This script was used to assist the buying up of smaller quantities of items to then sell in bulk.
# The results should help to select which items have the best bulk mark-up
# Once an item is chosen, place it within the bulk_live_search.py script to then live search bulk trades

import requests
import json
from time import sleep, strftime, gmtime
import settings


from log_bulk_live import logger
from playsound import playsound

itemsSet = [
            {"have":"chaos", "want":"gilded-bestiary-scarab","accounts":[]},
            {"have":"chaos", "want":"gilded-harbinger-scarab","accounts":[]},
            {"have":"chaos", "want":"bound-fossil","accounts":[]},
            {"have":"chaos", "want":"serrated-fossil","accounts":[]},
            {"have":"chaos", "want":"enchanted-fossil","accounts":[]},
            {"have":"chaos", "want":"gilded-breach-scarab","accounts":[]},
            {"have":"chaos", "want":"gilded-sulphite-scarab","accounts":[]},
            {"have":"chaos", "want":"gilded-legion-scarab","accounts":[]},
            {"have":"chaos", "want":"gilded-divination-scarab","accounts":[]},
            {"have":"chaos", "want":"fertile-catalyst","accounts":[]},
            {"have":"chaos", "want":"prismatic-catalyst","accounts":[]},
            {"have":"chaos", "want":"stacked-deck","accounts":[]},
           ]
quantSet = [3,10,20]

def stringify(numFloat):
    return str(round(numFloat,2))

print('{:50} {:15} {:15} {:15}'.format('Item', '3s', '10s', '20s'))

for items in itemsSet:
    statement = []
    for minimum in quantSet:
        logger.info("Have: " + items['have'] + " Want: " + items['want'])
        try:
            # ! Create the request payload to find accounts matching requiremnts
            payloadString = "{\"exchange\":{\"status\":{\"option\":\"online\"},\"have\":[\"" + items['have'] + "\"],\"want\":[\""+ items['want'] +"\"],\"minimum\":"+ str(minimum) +"}}"
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
            listingAccounts = accountsJSON['result'][:6] # Can make setting for how far down the listings to go

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

            average_cost = 0
            count = 0
            for listing in listingsList:
                accountID = listing['listing']['price']['item']['id']
                buyRatio = listing['listing']['price']['exchange']['amount']/listing['listing']['price']['item']['amount']
                logger.info(accountID + "(buyRatio): " + stringify(buyRatio))

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
                average_cost = ((average_cost * count) + listingDict['buyRatio'])/(count+1)
                count += 1
                # print('{} {:15} {:20} | {:30} : Stock:{:5} Price:{:4}'.format(strftime("%H:%M:%S", gmtime()), listingDict['buyName'],listingDict['sellerName'],listingDict['sellerIGN'],stringify(listingDict['stock']),stringify(listingDict['buyRatio'])))
                # print(strftime("%H:%M:%S", gmtime()) + ": NEW " + listingDict['buyName'] + " listing from: " + listingDict['sellerName'] + " | " + listingDict['sellerIGN'] + " | Stock:" + stringify(listingDict['stock']) + " | Price:" +  stringify(listingDict['buyRatio']))
            statement.append(stringify(average_cost))
        except KeyError:
            print("Error with: " + " -> ".join(items))
            logger.error("Error with: " + " -> ".join(items))
    print('{:50} {:15} {:15} {:15}'.format(items['want'], statement[0], statement[1], statement[2]))
playsound('smw_coin.wav', False)