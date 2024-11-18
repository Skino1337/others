import bet_manager
import time
import threading
import requests
import random
import copy

import utils
import program
import server
import harvesters

import asyncio
import discord_bot

from bet_manager import g_readyBetList


# g_cookies = {'ipp_key': '1531848059502/bjtzpNbvQ1j7GXMNjLbjbQ==',
#              'ipp_uid1': '1531848059501',
#              'ipp_uid2': 'mJ2glmGJNvWCH0hd/1zDZTNiy9df5OPAIKbz7Ig=='}



# Логин: lenta_all_001
# Пароль: 4522026
# mail: a6138297@nwytg.net

g_login = 'lenta_all_001'
g_cookies = {'ipp_key': '1533325130737/7TgodLbOqc0113Z6FeW4iQ==',
             'ipp_uid1': '1531410332742',
             'ipp_uid2': 'dhZlv0YXoWnZP029/SekNcpVFxKn3CVCI7C5LBQ==',
             'rerf': 'AAAAAFtHd5x3F3muA7VUAg==',
             'autotimezone': '3',
             'PHPSESSID': 'ligknuk53em5sm6ghb6qhanrm5',

             'dle_user_id': '894899',
             'login_user_token': '6f4ce55e6cfa25d28231ba677b66027b'}

# taked from sniffer Microsoft Network Monitor 3.4 after x100 try from BlueStacks emulater and vprognoze amdroid app
g_getReqQuery = {'action': 'get_fav_rss',
                 'type': 'rss',
                 'user_token_id': '894899',
                 'page': '0',
                 'user_token': 'ad335f3acc26ed3f6561d14b116b779c'}


g_wallBets = []

# exp https://vprognoze.ru/user/Snatch_bets/
g_userBetList = [#{'userName': 'polaris', 'bets': [],
                 # 'places': [{'type': 'profile', 'url': 'https://vprognoze.ru/user/polaris/'}]},
                 {'userName': 'ХАЙБЕРИ', 'bets': [],
                 'places': [{'type': 'profile', 'url': 'https://vprognoze.ru/user/%D5%E0%E9%E1%E5%F0%E8/'}]},
                 {'userName': 'AD1978', 'bets': [],
                  'places': [{'type': 'profile', 'url': 'https://vprognoze.ru/user/AD1978/'}]},
                 {'userName': 'BetForever', 'bets': [],
                 'places': [{'type': 'profile', 'url': 'https://vprognoze.ru/user/BetForever/'}]},
                 {'userName': 'cruseiter', 'bets': [],
                 'places': [{'type': 'profile', 'url': 'https://vprognoze.ru/user/cruseiter/'}]},
                 {'userName': 'daradat', 'bets': [],
                 'places': [{'type': 'profile', 'url': 'https://vprognoze.ru/user/daradat/'}]},
                 {'userName': 'dropshot', 'bets': [],
                 'places': [{'type': 'profile', 'url': 'https://vprognoze.ru/user/dropshot/'}]},
                 {'userName': 'Kasper', 'bets': [],
                 'places': [{'type': 'profile', 'url': 'https://vprognoze.ru/user/Kasper/'}]},
                 {'userName': 'kladas', 'bets': [],
                 'places': [{'type': 'profile', 'url': 'https://vprognoze.ru/user/kladas/'}]},
                 {'userName': 'mikola_minsk', 'bets': [],
                 'places': [{'type': 'profile', 'url': 'https://vprognoze.ru/user/mikola_minsk/'}]},
                 {'userName': 'montechristo', 'bets': [],
                 'places': [{'type': 'profile', 'url': 'https://vprognoze.ru/user/montechristo/'}]},
                 {'userName': 'niculin-st', 'bets': [],
                 'places': [{'type': 'profile', 'url': 'https://vprognoze.ru/user/niculin-st/'}]},
                 {'userName': 'Road+to+Australia', 'bets': [],
                 'places': [{'type': 'profile', 'url': 'https://vprognoze.ru/user/Road+to+Australia/'}]},
                 {'userName': 'RunnerUp', 'bets': [],
                 'places': [{'type': 'profile', 'url': 'https://vprognoze.ru/user/RunnerUp/'}]},
                 {'userName': 'shulza', 'bets': [],
                 'places': [{'type': 'profile', 'url': 'https://vprognoze.ru/user/shulza/'}]},
                 {'userName': 'skabinov', 'bets': [],
                 'places': [{'type': 'profile', 'url': 'https://vprognoze.ru/user/skabinov/'}]},
                 {'userName': 'Snatch_bets', 'bets': [],
                 'places': [{'type': 'profile', 'url': 'https://vprognoze.ru/user/Snatch_bets/'}]},
                 {'userName': 'Sork', 'bets': [],
                 'places': [{'type': 'profile', 'url': 'https://vprognoze.ru/user/Sork/'}]},
                 {'userName': 'Unnick', 'bets': [],
                 'places': [{'type': 'profile', 'url': 'https://vprognoze.ru/user/Unnick/'}]},
                 {'userName': 'x_CrackkeR_x', 'bets': [],
                 'places': [{'type': 'profile', 'url': 'https://vprognoze.ru/user/x_CrackkeR_x/'}]},
                 {'userName': 'Zelezobeton', 'bets': [],
                 'places': [{'type': 'profile', 'url': 'https://vprognoze.ru/user/Zelezobeton/'}]},
                 {'userName': 'БИНЬЗЫОНГ', 'bets': [],
                 'places': [{'type': 'profile', 'url': 'https://vprognoze.ru/user/%C1%E8%ED%FC%E7%FB%EE%ED%E3/'}]},
                 {'userName': 'SPORTWIN', 'bets': [],
                 'places': [{'type': 'profile', 'url': 'https://vprognoze.ru/user/SPORTWIN/'}]},
                 {'userName': 'toponerus', 'bets': [],
                 'places': [{'type': 'profile', 'url': 'https://vprognoze.ru/user/toponerus/'}]},
                 {'userName': 'icetips', 'bets': [],
                 'places': [{'type': 'profile', 'url': 'https://vprognoze.ru/user/icetips/'}]},
                 {'userName': 'JOXY', 'bets': [],
                 'places': [{'type': 'profile', 'url': 'https://vprognoze.ru/user/joxy/'}]},
                 {'userName': 'skorpion85', 'bets': [],
                 'places': [{'type': 'profile', 'url': 'https://vprognoze.ru/user/skorpion85/'}]},
                 {'userName': 'CAPPERMAN', 'bets': [],
                 'places': [{'type': 'profile', 'url': 'https://vprognoze.ru/user/CAPPERMAN/'}]},
                 {'userName': 'WhiteHorse84', 'bets': [],
                 'places': [{'type': 'tourney', 'url': 'https://vprognoze.ru/?do=cmp&action=rating&cid=514&uid=242643'}]},
                 {'userName': 'HukyJIuH', 'bets': [],
                 'places': [{'type': 'tourney', 'url': 'https://vprognoze.ru/?do=cmp&action=rating&cid=462&uid=868156'}]}]

'''
Проход дальше 1-я команда @ 2.47
1-й тайм ТМ (0.5) @ 2.30
Обе команды забьют: Да @ 1.71
Точный счет 2:0 @ 1.50
2-й тайм ТБ (1) @ 1.84
'''
def parseBet(bet):
    betInfo = {'coef': None, 'reverse': None, 'team': None, 'part': None,
               'win': None, 'win-type': None, 'draw': None, 'win-draw': None, 'win-win': None,
               'win-handicap': None, 'handicap-type': None, 'handicap': None,
               'total-points': None, 'total-points-direction': None,
               'total-points-type': None, 'total-points-number': None}

    betParts = bet['bet'].split('@')
    if len(betParts) != 2:
        utils.log('wrong parts count from bet split at "@", bet: ' + str(bet['bet']))
        return None

    betResult = betParts[0].strip()
    betCoef = betParts[1].strip()

    betInfo['coef'] = utils.toFloat(betCoef)
    if betInfo['coef'] is None:
        utils.log('cant convert coef to float, bet: ' + str(betCoef))
        return None

    if not (1.2 < betInfo['coef'] < 2.5):
        utils.log('worng coef (1.2 < ' + str(betInfo['coef']) + ' < 2.5), bet: ' + str(betCoef))
        return None

    asian = False
    if 'Азиатская' in betResult:
        asian = True
        betResult = betResult.replace('Азиатская', '')
        utils.log('ASIAN HAND DETECTED!!!! CHECK BETINFO!!, bet: ' + str(betResult))

    if 'Проход дальше' in betResult:
        if '1-я' in betResult:
            betInfo['team'] = 1
        elif '2-я' in betResult:
            betInfo['team'] = 2
        betInfo['win'] = True
        betInfo['win-type'] = 'total-win'
        return betInfo
    elif betResult == 'П1':
        betInfo['win'] = True
        betInfo['win-type'] = 'normal-time'
        betInfo['team'] = 1
        return betInfo
    elif betResult == 'П2':
        betInfo['win'] = True
        betInfo['win-type'] = 'normal-time'
        betInfo['team'] = 2
        return betInfo
    elif betResult == 'Ничья':
        betInfo['draw'] = True
        return betInfo
    elif betResult == 'Двойной шанс X2':
        betInfo['win-draw'] = True
        betInfo['team'] = 2
        return betInfo
    elif betResult == 'Двойной шанс 1X':
        betInfo['win-draw'] = True
        betInfo['team'] = 1
        return betInfo
    elif betResult == 'Двойной шанс 12':
        betInfo['win-win'] = True
        return betInfo
    elif 'ФОРА' in betResult:
        # TODO ---------------------------------------------------------------------------------------------------------
        # + ФОРА2 (1)
        # + ФОРА2 по геймам (-2)
        # - 2-я партия ФОРА2 (7.5)
        # - 1-я партия ФОРА2 (-2.5)
        betResultParts = betResult.split(' ')
        betResultPartsLenght = len(betResultParts)

        betResultTeam = None
        betResultHandicap = None
        betResultHandicapPart = None
        betResultHandicapType = None
        if betResultPartsLenght == 2:
            betResultTeam = betResultParts[0]
            betResultHandicap = betResultParts[1]
            betResultHandicap = betResultHandicap.strip('( )')
        elif betResultPartsLenght == 4:
            if 'ФОРА' in betResultParts[0]:
                betResultTeam = betResultParts[0]
                betResultHandicap = betResultParts[3]
                betResultHandicap = betResultHandicap.strip('( )')
                betResultHandicapType = betResultParts[2]
                betResultHandicapType = betResultHandicapType[:-2]
                betInfo['handicap-type'] = betResultHandicapType
            elif '-' in betResultParts[0]:
                betResultTeam = betResultParts[2]
                betResultHandicap = betResultParts[3]
                betResultHandicap = betResultHandicap.strip('( )')
                betResultHandicapPart = betResultParts[0]
                if '1' in betResultHandicapPart:
                    betInfo['part'] = 1
                elif '2' in betResultHandicapPart:
                    betInfo['part'] = 2
                elif '3' in betResultHandicapPart:
                    betInfo['part'] = 3
                elif '4' in betResultHandicapPart:
                    betInfo['part'] = 4
        else:
            utils.log('wrong parts count from bet result split at <SPACE>, bet: ' + str(betResult))
            return None

        betInfo['handicap'] = utils.toFloat(betResultHandicap)
        if betInfo['handicap'] is None:
            utils.log('cant convert handicap to float, bet: ' + str(betResultHandicap))
            return None

        if asian:
            hand = betInfo['handicap']
            if hand > 0:
                hand = hand + 0.25
                betInfo['coef'] = betInfo['coef'] - (betInfo['coef'] * 0.25)
            else:
                hand = hand - 0.25
                betInfo['coef'] = betInfo['coef'] + (betInfo['coef'] * 0.25)
            betInfo['handicap'] = hand

        if '1' in betResultTeam:
            betInfo['team'] = 1
        elif '2' in betResultTeam:
            betInfo['team'] = 2
        else:
            utils.log('cant parse handicap, bet: ' + str(betResultTeam))
            return None

        betInfo['win-handicap'] = True

        return betInfo
    elif 'ТМ' in betResult or 'ТБ' in betResult or 'Тотал' in betResult:
        # TODO ---------------------------------------------------------------------------------------------------------
        # + ТБ по очкам (96.5) @ 1.91
        # + ИТМ1 (12.5) @ 1.95
        # + Тотал по геймам меньше (21.5) @ 1.92
        betResultParts = betResult.split(' ')
        betResultPartsLenght = len(betResultParts)

        betResultDirection = None
        betResultPoints = None
        betResultPointsType = None
        if betResultPartsLenght == 2:
            betResultDirection = betResultParts[0]
            betResultPoints = betResultParts[1]
            betResultPoints = betResultPoints.strip('( )')
        elif betResultPartsLenght == 4:
            betResultDirection = betResultParts[0]
            betResultPoints = betResultParts[3]
            betResultPoints = betResultPoints.strip('( )')
            betResultPointsType = betResultParts[2]
            betResultPointsType = betResultPointsType[:-2]
            betInfo['total-points-type'] = betResultPointsType
        elif betResultPartsLenght == 5:
            betResultDirection = betResultParts[3]
            betResultPoints = betResultParts[4]
            betResultPoints = betResultPoints.strip('( )')
            betResultPointsType = betResultParts[2]
            betResultPointsType = betResultPointsType[:-2]
            betInfo['total-points-type'] = betResultPointsType
        else:
            utils.log('wrong parts count from bet result split at <SPACE>, bet: ' + str(bet))
            return None

        betInfo['total-points-number'] = utils.toFloat(betResultPoints)
        if betInfo['total-points-number'] is None:
            utils.log('cant convert total points number to float, bet: ' + str(bet))
            return None

        if 'ИТ' in betResultDirection:
            if '1' in betResultDirection:
                betInfo['team'] = 1
            elif '2' in betResultDirection:
                betInfo['team'] = 2

        if 'ТМ' in betResultDirection or 'меньше' in betResultDirection:
            betInfo['total-points-direction'] = 'under'
        elif 'ТБ' in betResultDirection or 'больше' in betResultDirection:
            betInfo['total-points-direction'] = 'over'
        else:
            utils.log('cant parse bet result with total points, bet: ' + str(bet))
            return None

        betInfo['total-points'] = True

        return betInfo
    else:
        utils.log('cant parse bet result, bet: ' + str(bet))
        return None

    return None

def getUserProfileBets(url):
    htmlData = requests.get(url, cookies=g_cookies).text
    #utils.log(htmlData)

    htmlData = utils.getDataBetween(htmlData, 'user_info', 'profileShowPageTips')
    userBets = []
    htmlDataBetList = utils.getDataBetween(htmlData, 'lastprognoz__bk', 'tips-desc_content', array=True)
    for htmlDataBet in htmlDataBetList:
        if 'Экспресс' in htmlDataBet:
            continue
        #utils.log(htmlDataBet)
        dateDay = utils.getDataBetween(htmlDataBet, '>', '<', jumps=['date', '>'])
        dateTime = utils.getDataBetween(htmlDataBet, '>', '<', jumps=['date', '>', '>', '>'])
        gameName = utils.getDataBetween(htmlDataBet, '>', '<', jumps=['match-name', '>'])
        sportType = utils.getDataBetween(htmlDataBet, '>', '.', jumps=['match-champ'])
        bet = utils.getDataBetween(htmlDataBet, '>', '<', jumps=['match-champ', 'text-center'])

        userBets.append({'gameDate': dateDay + ' ' + dateTime, 'gameName': gameName, 'sportType': sportType,
                         'bet': bet, 'betInfo': None})

    return userBets

def getMobileWallBets():
    query = {'action': 'get_fav_rss',
                     'type': 'rss',
                     'user_token_id': '894899',
                     'page': '0',
                     'user_token': 'ad335f3acc26ed3f6561d14b116b779c'}
    headers = {'Accept-Charset': 'UTF-8', 'ContentType': 'application/json;charset=UTF-8',
               'gmt': '3', 'UserAgent': 'okhttp/3.3.0', 'HeaderEnd': 'CRLF'}

    betsFromAllPages = []
    pageCount = 0
    isAllBets = False
    while not isAllBets:
        query['page'] = str(pageCount)
        request = None
        try:
            request = requests.get('https://vprognoze.ru/api/feed_android_test.php/', params=query, headers=headers)
        except:
            utils.log('[HARVESTERS.VPROGNOZE] requests.get error: ' + str(request))
            return None

        jsonData = None
        try:
            jsonData = request.json()
        except:
            utils.log('No JSON object could be decoded: ' + str(request.text))
            return None

        if 'data' not in jsonData:
            utils.log('jsonData has no have "data" key: ' + str(jsonData))
            return None

        bets = []
        for bet in jsonData['data']:
            coef = utils.toFloat(bet['kf'])
            if not (coef is not None and 1.3 < coef < 3.0):
                continue
            if not utils.checkRelevanceDate(bet['date']):
                isAllBets = True
                continue
            if len(bet['odds']) > 1:
                continue
            date = utils.dateFromTimestamp(bet['date'])

            # # to do all today bets
            # day = date[0:2]
            # if day != '07':
            #     utils.log('wrong day: ' + str(date))
            #     continue

            if 'Софтбол' in bet['league']:
                bet['league'] = bet['league'].replace('Бейсбол. Софтбол.', 'Софтбол.')
            sportPathParts = bet['league'][0].split('.', maxsplit=1)
            sportType = sportPathParts[0].strip()
            gamePath = sportPathParts[1].strip()
            # bk = utils.getDataBetween(bet['link_kf'], '/', '/', jumps=['bk'])
            # if bk == '12':
            #     bk = 'marathonbet'

            _bet = str(bet['odds'][0]) + ' @ ' + str(bet['kf'])

            bets.append({'sources': 'vprognoze / ' + bet['author'], 'gameDate': date,
                         'gameName': bet['command'][0]['home'] + ' - ' + bet['command'][0]['away'],
                         'sportType': sportType, 'gamePath': gamePath, 'bk': None, 'bet': _bet, 'betInfo': None})

            #utils.log(bets[len(bets) - 1])

        pageCount = pageCount + 1
        betsFromAllPages.extend(bets)
        if not isAllBets:
            time.sleep(random.uniform(1.00, 2.00))
        else:
            break

    return betsFromAllPages

def getWallBets():
    htmlData = requests.get('https://vprognoze.ru/lenta/', cookies=g_cookies).text
    if g_login not in htmlData:
        utils.log('vprognoze unlogin')
        return None
    # utils.log(htmlData)

    bets = []
    htmlDataBetList = utils.getDataBetween(htmlData, 'MenuLentaTipsBuild', '</tr>', array=True)
    for htmlDataBet in htmlDataBetList:
        if 'Экспресс' in htmlDataBet:
            continue
        # utils.log(str(htmlDataBet))

        author = utils.getDataBetween(htmlDataBet, '>', '<', jumps=['avtor'])

        dateDay = utils.getDataBetween(htmlDataBet, '>', '<', jumps=['target', 'target'])
        dateTime = utils.getDataBetween(htmlDataBet, '>', '<', jumps=['target', 'target', '>'])

        gameName = utils.getDataBetween(htmlDataBet, '>', '<', jumps=['title'])
        gameName = utils.cutBrackerts(gameName)

        sportType = utils.getDataBetween(htmlDataBet, '"', '.', jumps=['title'])
        gamePath = utils.getDataBetween(htmlDataBet, '. ', '"', jumps=['title'])

        bet = utils.getDataBetween(htmlDataBet, '>', '<', jumps=['align', 'align', '>'])

        bets.append({'sources': 'vprognoze / ' + author, 'gameDate': dateDay + ' ' + dateTime, 'gameName': gameName,
                         'sportType': sportType, 'gamePath': gamePath, 'bk': None, 'bet': bet, 'betInfo': None})

        # utils.log(str(bets[len(bets) - 1]))

    return bets

def getUserTourneyBets(userTourneyUrl):
    htmlData = requests.get(userTourneyUrl, cookies=g_cookies).text
    htmlData = utils.getDataBetween(htmlData, 'oddstable', '</table>')

    userTourneyBets = []
    htmlDataBetList = utils.getDataBetween(htmlData, 'bgr_', '</tr>', array=True)
    for htmlDataBet in htmlDataBetList:
        classSteps = ['class' for i in range(1)]
        classSteps.extend(['>'])
        author = utils.getDataBetween(htmlDataBet, '>', '<', jumps=classSteps)
        dateDay = utils.getDataBetween(htmlDataBet, '>', '<', jumps=['class' for i in range(4)])
        classSteps = ['class' for i in range(4)]
        classSteps.extend(['>'])
        dateTime = utils.getDataBetween(htmlDataBet, '>', '<', jumps=classSteps)
        game = utils.getDataBetween(htmlDataBet, '>', '<', jumps=['class' for i in range(6)])
        bk = utils.getDataBetween(htmlDataBet, 'title="', '"', jumps=['class' for i in range(7)])
        sportType = utils.getDataBetween(htmlDataBet, '<span>', '</span>', jumps=['class' for i in range(8)])
        gamePath = utils.getDataBetween(htmlDataBet, '>', '<', jumps=['class' for i in range(9)])
        gamePath = gamePath[2:]
        bet = utils.getDataBetween(htmlDataBet, '>', '<', jumps=['class' for i in range(10)])

        userTourneyBets.append({'sources': 'vprognoze / ' + author, 'gameDate': dateDay + ' ' + dateTime, 'gameName': game,
                                'sportType': sportType, 'gamePath': gamePath, 'bk': bk, 'bet': bet, 'betInfo': None})

    return userTourneyBets

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

def loop():
    global g_wallBets

    time.sleep(2)

    while True:
        if server.isBrowserReadyToBet():
            time.sleep(random.uniform(1.00, 2.00))
        else:
            time.sleep(random.uniform(1.00 * 10, 2.00 * 10))

        bets = getMobileWallBets()
        if bets is None:
            continue
        if len(g_wallBets) < 1:
            g_wallBets = copy.deepcopy(bets)
            continue
        newBets = compareBets(g_wallBets, bets)

        # if len(newBets) < 1:
        #     utils.log('no new bets')

        for newBet in newBets:
            g_wallBets.append(newBet)

            if not server.g_isBrowserConnected:
                discord_bot.discordWriteMessage('New bet:\n' + 'sources: ' + newBet['sources'])

            betInfo = parseBet(newBet)
            if betInfo is None:
                utils.log('cant parse bet: \n' + str(newBet))
                if server.g_isBrowserConnected:
                    discord_bot.discordWriteMessage('Cant parse bet:\n' + 'sources: ' + newBet['sources'] + '\n'
                                                    + 'gameName: ' + newBet['gameName'] + '\n'
                                                    + 'bet: ' + newBet['bet'])
                continue
            g_wallBets[len(g_wallBets) - 1]['betInfo'] = betInfo

            utils.log('NEW BET: \n' + str(newBet))

            g_readyBetList.append(newBet)

            time.sleep(1)

        time.sleep(1)

def myCode():

    time.sleep(2.0)

    utils.log('!!!FOR TEST ONLY!!! myCode in hervesters.vprognoze init !!!FOR TEST ONLY!!!')

    testBet = {'gameName': 'Э.Маррэй - К.Эдмунд.', 'sportType': 'Теннис', 'bet': 'П1 @ 2.23'}

    cBets = copy.deepcopy(g_userBetList[0]['bets'])
    rBets = copy.deepcopy(g_userBetList[0]['bets'])
    rBets.append(testBet)

    time.sleep(4)

    newbet = compareBets(cBets, rBets)

    betinfo = parseBet(testBet)
    if betinfo is None:
        utils.log('parseBet() return None, bet: \n' + str(testBet))
        return
    testBet['betInfo'] = betinfo

    g_readyBetList.append(testBet)
    utils.log('bet_manager.addBet(testBet)')

def init():
    utils.log('harvesters.vprognoze start')
    threading.Thread(target=loop, name='harvesters.vprognoze').start()
    #threading.Thread(target=myCode, name='harvesters.vprognoze myCode').start()