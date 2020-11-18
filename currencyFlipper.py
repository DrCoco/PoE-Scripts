# Author: Kiran Chandradevan
# This script searches the current bulk listings and calculates the returns from flipping the currency
# It support two-way and three-way flips e.g. chaos -> fuse -> exalt
# Initially planned for it to create an average from the top 10 listings
# Without an ability to filter accounts posting fake listings, the usefulness of this script is limited

import requests
import json
from time import sleep
from log_currency import logger
import settings

itemsSet = [ ['chaos', 'regret'],
            ['chaos', 'fuse'],
            ['chaos', 'p'],
            # ['chaos', 'stacked'],
            ['chaos', 'alch'],
            ['chaos', 'chrome'],
            # ['chaos', 'regal'],
            ['chaos', 'alt'],
            # ['chaos', 'aug'],    
            # ['chaos', 'vaal'],
            # ['exa', 'fuse'],
            # ['chaos','exa'],
            # ['chaos', 'apprentice-sextant','exa'],
            # ['chaos', 'journeyman-sextant','exa'],
            # ['chaos', 'master-sextant','exa'],
            # ['chaos','divine','exa'],
            ['chaos','chisel'],
            # ['chaos','exa','chisel'],
            ['chaos', 'fuse', 'exa']]

def stringify(numFloat):
    return str(round(numFloat,2))

for items in itemsSet:
    logger.info("Current item set: " + ",".join(items))
    try:
        compareList = []
        for item in range(len(items)):
            # ! Create the request payload to find accounts matching requiremnts
            payloadString = "{\"exchange\":{\"status\":{\"option\":\"online\"},\"have\":[\"" + items[(item+1)%len(items)] + "\"],\"want\":[\""+ items[item] +"\"]}}"
            logger.info("payloadString: " + payloadString)
            payloadJSON = json.loads(payloadString)
            accountsResponse = requests.post('https://www.pathofexile.com/api/trade/exchange/' + settings.league,json=payloadJSON)
            accountsJSON = accountsResponse.json()

            if 'error' in accountsJSON:
                logger.error(accountsJSON['error']['message'])
            listingsID = accountsJSON['id']
            logger.info("Listings ID: " + listingsID)
            numListings = accountsJSON['total']
            logger.info("Number of Listings: " + stringify(numListings))
            listingAccounts = accountsJSON['result'][15:16] # Can make setting for how far down the listings to go

            if len(listingAccounts) == 1:
                listingsURL = "https://www.pathofexile.com/api/trade/fetch/" + listingAccounts[0]
                listingsURL += "?query=" + listingsID + "&exchange"
                logger.info("Pulling listings from: " + listingsURL)

                listingsResponse = requests.get(listingsURL)
                listingsJSON = listingsResponse.json()
                listingsList = listingsJSON['result']
                logger.info(json.dumps(listingsJSON))

                for listing in listingsList:
                    listingDict = {}
                    listingDict['sell'] = listing['listing']['price']['item']['amount']
                    listingDict['buy'] = listing['listing']['price']['exchange']['amount']
                    listingDict['stock'] = listing['listing']['price']['item']['stock']
                    listingDict['sellName'] = listing['listing']['price']['exchange']['currency']
                    listingDict['buyName'] = listing['listing']['price']['item']['currency']
                    listingDict['buyRatio'] = listingDict['buy']/listingDict['sell']
                    listingDict['sellRatio'] = listingDict['sell']/listingDict['buy']
                    compareList.append(listingDict)
                    logger.info("Appended: " + json.dumps(listingDict))
            else:
                listingDict = {}
                listingDict['sell'] = 1
                listingDict['buy'] = 1
                listingDict['stock'] = 1
                listingDict['sellName'] = "none"
                listingDict['buyName'] = "none"
                listingDict['buyRatio'] = listingDict['buy']/listingDict['sell']
                listingDict['sellRatio'] = listingDict['sell']/listingDict['buy']
                compareList.append(listingDict)
                logger.info("Appended: " + json.dumps(listingDict))




        buy = compareList[0]['buyRatio']
        if len(compareList) > 2:
            buy *= compareList[2]['buyRatio']
        logger.debug("Buy calculated at: " + stringify(buy))
        sell = compareList[1]['sellRatio']
        logger.debug("Sell calculated at: " + stringify(sell))
        profit = buy - sell
        logger.debug("Profit calculated at: " + stringify(profit))
        profitMargin = profit*100/sell
        logger.debug("Profit Margin calculated at: " + stringify(profitMargin))

        print("Flip: " + " -> ".join(items))
        logger.info("Flip: " + " -> ".join(items))
        
        print("Sell " + items[0] + " for " + stringify(compareList[0]['buyRatio']) + " " + items[1] + " (" + stringify(compareList[0]['sell']) + " : " + stringify(compareList[0]['buy']) + ")")
        print("Sell " + stringify(compareList[1]['sellRatio']) + " " + items[1] + " for " + items[2%len(compareList)] + " (" + stringify(compareList[1]['sell']) + " : " + stringify(compareList[1]['buy']) + ")")
        logger.info("Sell " + items[0] + " for " + stringify(compareList[0]['buyRatio']) + " " + items[1] + " (" + stringify(compareList[0]['sell']) + " : " + stringify(compareList[0]['buy']) + ")")
        logger.info("Sell " + stringify(compareList[1]['sellRatio']) + " " + items[1] + " for " + items[2%len(compareList)] + " (" + stringify(compareList[1]['sell']) + " : " + stringify(compareList[1]['buy']) + ")")

        if len(items) > 2:
            print("Sell " + items[2] + " for " + stringify(compareList[2]['buyRatio']) + " " + items[0] + " (" + stringify(compareList[2]['sell']) + " : " + stringify(compareList[2]['buy']) + ")")
            logger.info("Sell " + items[2] + " for " + stringify(compareList[2]['buyRatio']) + " " + items[0] + " (" + stringify(compareList[2]['sell']) + " : " + stringify(compareList[2]['buy']) + ")")

        print("Profit: " + stringify(profit) + " " + items[1] + " (" + stringify(profit/compareList[0]['buyRatio']) + " chaos)")
        print("Profit Margin: " + stringify(profitMargin) + "%")
        logger.info("Profit: " + stringify(profit) + " " + items[1] + " (" + stringify(profit/compareList[0]['buyRatio']) + " chaos)")
        logger.info("Profit Margin: " + stringify(profitMargin) + "%")
        if profitMargin > 0:
            print("Profitable")
            logger.info("Profitable")
        else:
            print("Not profitable!")
            logger.info("Not profitable")
        print("")
        sleep(1)
    except KeyError:
        print("Error with: " + " -> ".join(items))
        logger.error("Error with: " + " -> ".join(items))


