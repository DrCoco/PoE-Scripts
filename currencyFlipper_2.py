# Author: Kiran Chandradevan
# Second iteration of the currency flipper script
# This one put the flips in a nice table format
import requests
import json
from time import sleep
from log_currency import logger
import settings
import pandas as pd

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

df = pd.DataFrame(columns=['Flip','P%','Trade 1','Trade 2', 'Trade 3'])
logger.info("DataFrame created")

itemsSet = [['chaos', 'regret'],
            ['chaos', 'fuse'],
            ['chaos', 'p'],
            ['chaos', 'alch'],
            ['chaos', 'chrome'],
            ['chaos', 'regal'],
            ['chaos', 'alt'],
            ['chaos', 'aug'],
            ['chaos', 'vaal'],
            ['chaos', 'gcp'],
            ['exa', 'fuse'],
            ['chaos','exa'],
            ['chaos','chisel'],
            ['chaos', 'ancient-orb'],
            ['chaos', 'orb-of-annulment'],
            ['chaos', 'harbingers-orb'],
            ['chaos', 'tempering-catalyst'],
            ['chaos','intrinsic-catalyst'],
            ['chaos', 'perfect-fossil'],
            ['chaos', 'pristine-fossil'],
            ['chaos', 'master-sextant','exa'],
            ['chaos','divine','exa'],
            ['exa', 'fuse', 'chaos'],
            ['chaos','exa','chisel'],
            ['chaos', 'fuse', 'exa']]

def stringify(numFloat):
    return str(round(numFloat,2))

flipCount = 0
profitableCount = 0
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
            if numListings < 20:
                raise Exception('Low Confidence Flip')
            logger.info("Number of Listings: " + stringify(numListings))
            listingAccount = accountsJSON['result'][3] # Can make setting for how far down the listings to go

            if listingAccount:
                listingsURL = "https://www.pathofexile.com/api/trade/fetch/" + listingAccount
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

        flip = ",".join(items)
        trade1 = "{} {}:{} {}".format(items[0], stringify(compareList[0]['sell']), stringify(compareList[0]['buy']), items[1])
        trade2 = "{} {}:{} {}".format(items[1], stringify(compareList[1]['sell']), stringify(compareList[1]['buy']), items[2%len(compareList)])
        trade3 = ""
        if len(items) > 2:
            trade3 = "{} {}:{} {}".format(items[2], stringify(compareList[2]['sell']), stringify(compareList[2]['buy']), items[0])

        logger.info(flip)
        logger.info(trade1)
        logger.info(trade2)
        logger.info(trade3)
        sleep(1)
        if profitMargin > 0:
            dataList = [flip, int(profitMargin), trade1, trade2, trade3]
            df.loc[profitableCount] = dataList
            profitableCount += 1
    except KeyError:
        print("Error with: " + " -> ".join(items))
        logger.error("Error with: " + " -> ".join(items))
    except Exception:
        logger.error("Low Confidence: " + " -> ".join(items))

    flipCount += 1
    printProgressBar(flipCount, len(itemsSet), prefix='Flipper Progress',suffix='Complete',length=50)

df.sort_values(by=['P%'], inplace=True)
print(df)


