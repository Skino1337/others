import time
import threading
import requests
import random
import copy

import utils
import discord_bot


g_sportTypeList = [{'url': 'https://www.betonsuccess.ru/stavki-na-sport/besplatnye/19/futbol/', 'betList': []},
                   {'url': 'https://www.betonsuccess.ru/stavki-na-sport/besplatnye/20/tennis/', 'betList': []},
                   {'url': 'https://www.betonsuccess.ru/stavki-na-sport/besplatnye/3/basketbol/', 'betList': []},
                   {'url': 'https://www.betonsuccess.ru/stavki-na-sport/besplatnye/8/hokkej/', 'betList': []},
                   {'url': 'https://www.betonsuccess.ru/stavki-na-sport/besplatnye/9/bejsbol/', 'betList': []},
                   {'url': 'https://www.betonsuccess.ru/stavki-na-sport/besplatnye/12/gandbol/', 'betList': []}]


def getBets(sportType):
    request = None
    try:
        request = requests.get(sportType['url'])
    except:
        utils.log('[HARVESTERS.BETONSUCCESS] Error, requests.get() raise exception')
        return None
    request.encoding = 'cp1251'
    htmlData = request.text

    userWithProfitList = []
    userHeaderHtmlList = utils.getParsedData(htmlData, ['width:30px'], ['width:60px'], array=True)
    if userHeaderHtmlList is None:
        return None
    for userHeaderHtml in userHeaderHtmlList:
        profitPlanText = utils.getParsedData(userHeaderHtml, ['width:90px', '>'], ['<'])
        profitPlanText = utils.getParsedData(profitPlanText, ['+'], ['%'])
        profitPlanNum = utils.toFloat(profitPlanText)
        if profitPlanNum is None or profitPlanNum < 40:
            break

        ratingPositionText = utils.getParsedData(userHeaderHtml, ['>'], ['<'])
        ratingPositionNum = utils.toFloat(ratingPositionText)
        if ratingPositionNum is None or ratingPositionNum > 10:
            break

        userWithProfit = utils.getParsedData(userHeaderHtml, ['/sub/', '/'], ['.'])
        if userWithProfit is not None:
            userWithProfitList.append(userWithProfit)

    betList = []
    userBetHtmlList = utils.getParsedData(htmlData, ['class="sport'], ['darkred'], array=True)
    for userBetHtml in userBetHtmlList:
        author = utils.getParsedData(userBetHtml, ['/sub/', '/'], ['.'])
        if not (author and author in userWithProfitList):
            break

        type = utils.getParsedData(userBetHtml, ['>', '>'], ['<'])

        date = utils.getParsedData(userBetHtml, ['Событие', '>', '>'], ['&'])
        monthReplaceList = [' января ', ' февраля ', ' марта ', ' апреля ', ' мая ', ' июня ',
                            ' июля ', ' августа ', ' сентября ', ' октября ', ' ноября ', ' декабря ']
        for count, month in enumerate(monthReplaceList, start=1):
            if month in date:
                formatedMoth = str(count) if len(str(count)) == 2 else '0' + str(count)
                date = date.replace(month, '-' + formatedMoth + '-')
                break
        date = date.strip()
        date = date.replace(',', '')

        path = utils.getParsedData(userBetHtml, ['</div></div>'], ['<'])

        userBetHtml = utils.getParsedData(userBetHtml, ['event', 'event'], ['book'])

        name = utils.getParsedData(userBetHtml, ['>', '>', '>'], ['<'])

        result = utils.getParsedData(userBetHtml, ['outcome', '>'], ['<'])
        result = result if len(result) > 0 else None

        aux = utils.getParsedData(userBetHtml, ['event_aux', '>'], ['<'])
        aux = aux.strip()
        aux = aux if len(aux) > 0 else None

        coef = utils.getParsedData(userBetHtml, ['"odds"', '>', '>'], ['<'])
        coefFloat = utils.toFloat(coef)
        if coefFloat is None:
            utils.log('[HARVESTERS.BETONSUCCESS] Error, express?: ' + str(userBetHtml))


        betList.append({'sources': 'betonsuccess / ' + author, 'date': date, 'name': name, 'type': type,
                        'path': path, 'result': result, 'aux': aux, 'coef': coef, 'betInfo': None})

    return betList

def loop():
    while True:
        time.sleep(random.uniform(2, 5))
        for sportType in g_sportTypeList:
            time.sleep(random.uniform(2, 5))
            betList = getBets(sportType)
            if betList is None or len(betList) <= 0:
                continue
            if len(sportType['betList']) <= 0:
                sportType['betList'] = copy.deepcopy(betList)
                continue
            for bet in betList:
                if bet in sportType['betList']:
                    continue

                sportType['betList'].append(bet)

                discord_bot.discordWriteMessage('New bet for HAND INPUT:\n'
                                                + 'sources: ' + bet['sources'] + '\n'
                                                + 'date: ' + bet['date'] + '\n'
                                                + 'name: ' + bet['name'] + '\n'
                                                + 'type: ' + bet['type'] + '\n'
                                                + 'path: ' + bet['path'] + '\n'
                                                + 'result: ' + bet['result'] + '\n'
                                                + 'aux: ' + str(bet['aux']) + '\n'
                                                + 'coef: ' + str(bet['coef']) + '\n')

def init():
    utils.log('harvesters.betonsuccess start')
    threading.Thread(target=loop, name='harvesters.betonsuccess').start()

# init()
# time.sleep(999)