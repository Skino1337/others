import time
import threading
import requests
import random
import datetime

import utils
import server
import asyncio
import discord_bot
from bet_manager import g_readyBetList

g_userDataList = [{'name': '777oleg', 'rssUrl': 'https://prognozist.ru/user/777oleg/rss.xml',
                  'betLinkList': [], 'bets': []}]

'''
Индивидуальный тотал 1 Больше 2.5
Результат матча Суррей Старз
Победа с учетом форы Ухань Шанвэнь (-1)
Тотал меньше(5.5)
Победа с учетом форы Бернли до 23 (-1)
Гандикап Пярну Варпус(+1) @ 1.42
Тотал матча по очкам Больше 84.5 @ 1.88 cant parse total, wrong parts count from bet result split at <SPACE>
Победа с учетом форы по геймам Виртанен, Отто (+2)
'''

def parseBet(bet):
    betInfo = {'coef': None, 'reverse': None, 'team': None, 'part': None,
               'win': None, 'win-type': None, 'draw': None, 'win-draw': None, 'win-win': None,
               'win-handicap': None, 'handicap-type': None, 'handicap': None,
               'total-points': None, 'total-points-direction': None,
               'total-points-type': None, 'total-points-number': None}

    betParts = bet['bet'].split('@')
    if len(betParts) != 2:
        utils.log('wrong parts count from bet split at "@", bet: ' + str(bet))
        return None

    betResult = betParts[0].strip()
    betResultBefore = betResult
    betResult = utils.stringGarbageClear(betResult, garbageList=['в матче', 'матча', 'голов'])
    betResult = betResult.replace('(', ' ')
    betResult = betResult.replace(')', ' ')
    betCoef = betParts[1].strip()

    betInfo['coef'] = utils.toFloat(betCoef)
    if betInfo['coef'] is None:
        utils.log('cant convert coef to float, bet: ' + str(betCoef))
        return None

    if not (1.2 < betInfo['coef'] < 3.0):
        utils.log('worng coef (1.2 < ' + str(betInfo['coef']) + ' < 3.0), bet: ' + str(betCoef))
        return None

    betResult = betResult.lower()
    betResult = betResult.strip()
    while '  ' in betResult:
        betResult = betResult.replace('  ', ' ')

    gameName = bet['gameName']
    gameName = gameName.lower()
    gameName = utils.stringCutInitials(gameName)
    teamParts = gameName.split(' - ')
    teamString = None
    if len(teamParts) != 2:
        utils.log('wrong parts count from bet game name split at " - ", bet: ' + str(gameName))
        return None
    teamParts[0] = teamParts[0].strip()
    teamParts[1] = teamParts[1].strip()
    if teamParts[0] in betResult:
        betResult = betResult.replace(teamParts[0], ' 1 ')
        teamString = '1'
    elif teamParts[1] in betResult:
        betResult = betResult.replace(teamParts[1], ' 2 ')
        teamString = '2'



    # win
    betResult = betResult.replace('результат матча ', 'п')

    # total
    betResult = betResult.replace('индивидуальный тотал 1 больше', 'итб1')
    betResult = betResult.replace('индивидуальный тотал 2 больше', 'итб2')
    betResult = betResult.replace('индивидуальный тотал 1 меньше', 'итм1')
    betResult = betResult.replace('индивидуальный тотал 2 меньше', 'итм2')

    # handicap
    betResult = betResult.replace('победа с учетом форы ', 'фора')
    betResult = betResult.replace('гандикап ', 'фора')
    betResult = betResult.replace('фора ', 'фора')

    # total
    betResult = betResult.replace('тотал больше ', 'тб')
    betResult = betResult.replace('тотал меньше ', 'тм')

    while '  ' in betResult:
        betResult = betResult.replace('  ', ' ')

    betResultAfter = betResult
    utils.log('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!betResult before and after: ' + betResultBefore + ' > ' + betResultAfter)

    betResultParts = betResult.split(' ')
    betResultPartsLenght = len(betResultParts)

    if 'угл' in betResult:
        utils.log('worng betResult (угл), bet: ' + betResult)
        return None

    if betResult == 'п1':
        betInfo['win'] = True
        betInfo['win-type'] = 'main-time'
        betInfo['team'] = 1
        return betInfo
    elif betResult == 'п2':
        betInfo['win'] = True
        betInfo['win-type'] = 'main-time'
        betInfo['team'] = 2
        return betInfo
    elif 'фора' in betResult:
        betResultTeam = None
        betResultHandicap = None
        betResultHandicapPart = None
        betResultHandicapType = None
        if betResultPartsLenght == 2:
            betResultTeam = betResultParts[0]
            betResultHandicap = betResultParts[1]
            betResultHandicap = betResultHandicap.strip('( )')
        else:
            utils.log('wrong parts count from bet result split at <SPACE>, bet: ' + str(betResult))
            return None

        betInfo['handicap'] = utils.toFloat(betResultHandicap)
        if betInfo['handicap'] is None:
            utils.log('cant convert handicap to float, bet: ' + str(betResultHandicap))
            return None

        if '1' in betResultTeam:
            betInfo['team'] = 1
        elif '2' in betResultTeam:
            betInfo['team'] = 2
        else:
            utils.log('cant parse handicap, bet: ' + str(betResultTeam))
            return None

        betInfo['win-handicap'] = True

        return betInfo
    elif 'тм' in betResult or 'тб' in betResult:
        betResultDirection = None
        betResultPoints = None
        betResultPointsType = None
        if betResultPartsLenght == 2:
            betResultDirection = betResultParts[0]
            betResultPoints = betResultParts[1]
            betResultPoints = betResultPoints.strip('( )')
        else:
            utils.log('wrong parts count from bet result split at <SPACE>, bet: ' + str(betResult))
            return None

        betInfo['total-points-number'] = utils.toFloat(betResultPoints)
        if betInfo['total-points-number'] is None:
            utils.log('cant convert total points number to float, bet: ' + str(betResultPoints))
            return None

        if 'ИТ' in betResultDirection:
            if '1' in betResultDirection:
                betInfo['team'] = 1
            elif '2' in betResultDirection:
                betInfo['team'] = 2

        if 'ТМ' in betResultDirection:
            betInfo['total-points-direction'] = 'under'
        elif 'ТБ' in betResultDirection:
            betInfo['total-points-direction'] = 'over'
        else:
            utils.log('cant parse bet result with total points, bet: ' + str(betResultDirection))
            return None

        betInfo['total-points'] = True

        return betInfo
    else:
        utils.log('cant parse bet result, bet: ' + str(bet))
        return None

    return None

def compareBets(currentBets, recivedBets):
    retnList = []
    for rBet in recivedBets:
        isNewBet = True
        for cBet in currentBets:
            if rBet['gameName'] == cBet['gameName'] and rBet['bet'] == cBet['bet']:
                isNewBet = False
                break
        if isNewBet:
            retnList.append(rBet)
    return retnList

def getUserBets(userData):
    request = None
    try:
        request = requests.get(userData['rssUrl'])
    except:
        utils.log('[HARVESTERS.PROGNOZIST] requests.get error: ' + str(request))
        return None
    userRssHtmlData = request.text

    betList = []
    betLinkList = []
    itemHtmlList = utils.getDataBetween(userRssHtmlData, '<item>', '</item>', array=True)
    for itemHtml in itemHtmlList:
        if 'Платн' in itemHtml:
            continue
        betLink = utils.getDataBetween(itemHtml, '<link>', '</link>')
        betLinkList.append(betLink)

    if len(userData['betLinkList']) <= 0:
        userData['betLinkList'] = betLinkList
        return betList

    for betLink in betLinkList:
        #if betLink in userData['betLinkList']:
            #continue
        userData['betLinkList'].append(betLink)
        try:
            request = requests.get(betLink)
        except:
            utils.log('requests.get error: ' + str(request))
            return None
        betPageHtmlData = request.text
        betHtmlData = utils.getDataBetween(betPageHtmlData, 'block-ordinar-bet', 'block-ordinar-bankbet')

        author = userData['name']

        game = utils.getDataBetween(betHtmlData, '>', '<', jumps=['game'])

        date = utils.getDataBetween(betHtmlData, '>', '<', jumps=['match_start'])
        tDate = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M')
        date = tDate.strftime('%d-%m %H:%M')

        eventNameFull = utils.getDataBetween(betPageHtmlData, '"', '"', jumps=['SportsEvent', 'name', ':'])
        sportPathParts = eventNameFull.split('.', maxsplit=1)
        sportType = sportPathParts[0].strip()
        gamePath = sportPathParts[1].strip()

        bk = utils.getDataBetween(betHtmlData, ';', '&', jumps=['go-bk-btn', 'onclick'])

        betResult = utils.getDataBetween(betHtmlData, '<strong>', '</strong>')
        betResult = betResult.strip()

        betCoef = utils.getDataBetween(betHtmlData, 'Коэффициент', '<')
        betCoef = betCoef.strip(' :')

        betList.append({'sources': 'prognozist / ' + author, 'gameDate': date, 'gameName': game, 'sportType': sportType,
                     'gamePath': gamePath, 'bk': bk, 'bet': betResult + ' @ ' + betCoef, 'betInfo': None})

        time.sleep(random.uniform(1, 2))

    return betList

def loop():
    global g_userDataList

    while True:
        if server.isBrowserReadyToBet():
            r = random.uniform(1, 2)
            time.sleep(r)
        else:
            r = random.uniform(1, 2)
            time.sleep(r)
        for userData in g_userDataList:
            r = random.uniform(1, 2)
            time.sleep(r)
            bets = getUserBets(userData)
            if bets is None or len(bets) <= 0:
                continue
            newBets = compareBets(userData['bets'], bets)

            for newBet in newBets:
                userData['bets'].append(newBet)

                if not server.g_isBrowserConnected:
                    discord_bot.discordWriteMessage('New bet:\n' + 'sources: ' + newBet['sources'])

                betInfo = parseBet(newBet)
                if betInfo is None:
                    utils.log('cant parse bet: \n' + str(newBet))
                    if server.g_isBrowserConnected:
                        discord_bot.discordWriteMessage('Cant parse bet:\n' + 'sources: ' + newBet['sources'])
                    continue
                userData['bets'][len(userData['bets']) - 1]['betInfo'] = betInfo

                utils.log('NEW BET: \n' + str(newBet))

                g_readyBetList.append(newBet)



def init():
    utils.log('harvesters.prognozist start')
    threading.Thread(target=loop, name='harvesters.prognozist').start()