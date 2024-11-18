import requests
import requests.exceptions
import threading
import json
import datetime

import utils

g_marathonUrl = 'https://www.marathonbet.ru/'
g_sportTypeUrlList = []
g_handicaps = []
g_totals = []

def chooseBetterHandicap(betInfo):
    # 1.80 < 2.00 < 2.20
    minCoef = betInfo['coef'] - ((betInfo['coef'] - 1.00) * 0.20)
    maxCoef = betInfo['coef'] + ((betInfo['coef'] - 1.00) * 0.20)
    minHandicap = betInfo['handicap']
    maxHandicap = betInfo['handicap']
    if minHandicap > 0:
        # +50.0 < +50.0 < +50.0 => +45.0 < +50.0 < +55.0
        minHandicap = (minHandicap - (minHandicap * 0.10))
        maxHandicap = (maxHandicap + (maxHandicap * 0.10))
    else:
        # -50.0 < -50.0 < -40.0 => -55.0 < -50.0 < -45.0
        minHandicap = (minHandicap + (minHandicap * 0.10))
        maxHandicap = (maxHandicap - (maxHandicap * 0.10))
    currentSetup = {'handicap': minHandicap, 'coef': betInfo['coef'], 'keys': []}
    for setup in g_handicaps:
        if minCoef < setup['coef'] < maxCoef:
            if minHandicap < setup['handicap'] < maxHandicap:
                if setup['handicap'] > currentSetup['handicap']:
                    currentSetup = setup

    utils.log('better setup (handicap: '
              + str(minHandicap) + ' < ' + str(currentSetup['handicap']) + ' < ' + str(maxHandicap)
              + ', coef: ' + str(minCoef) + ' < ' + str(currentSetup['coef']) + ' < ' + str(maxCoef) + ')')
    if len(currentSetup['keys']) < 2:
        currentSetup = None

    return currentSetup

def chooseBetterTotal(betInfo):
    # 1.80 < 2.00 < 2.20
    minCoef = betInfo['coef'] - ((betInfo['coef'] - 1.00) * 0.20)
    maxCoef = betInfo['coef'] + ((betInfo['coef'] - 1.00) * 0.20)
    minTotal = betInfo['total-points-number']
    maxTotal = betInfo['total-points-number']
    # 100.0 < 100.0 < 100.0 => 90.0 < 100.0 < 110.0
    if betInfo['total-points-direction'] == 'over':
        minTotal = minTotal + (minTotal * 0.10)
        maxTotal = maxTotal - (maxTotal * 0.10)
    else:
        minTotal = minTotal - (minTotal * 0.10)
        maxTotal = maxTotal + (maxTotal * 0.10)
    currentSetup = {'total': minTotal, 'dir': betInfo['total-points-direction'],
                    'coef': betInfo['coef'], 'keys': []}

    for setup in g_totals:
        if minCoef < setup['coef'] < maxCoef:
            if currentSetup['dir'] == 'over':
                if minTotal > setup['total'] > maxTotal:
                    if setup['total'] > currentSetup['total']:
                        continue
            else:
                if minTotal < setup['total'] < maxTotal:
                    if setup['total'] < currentSetup['total']:
                        continue

            currentSetup = setup

    utils.log('better setup (total ' + currentSetup['dir'] + ': '
              + str(minTotal) + ' <> ' + str(currentSetup['total']) + ' <> ' + str(maxTotal)
              + ', coef: ' + str(minCoef) + ' < ' + str(currentSetup['coef']) + ' < ' + str(maxCoef) + ')')

    if len(currentSetup['keys']) < 2:
        currentSetup = None

    return currentSetup

def getShortcutLinkKey(htmlData, key):
    buttonList = utils.getDataBetween(htmlData, '<td', '</td>', array=True)
    filterList = ['shortcutLink_', key]
    for filter in filterList:
        buttonList = [x for x in buttonList if filter in x]

    if len(buttonList) != 1:
        utils.log('cant getShortcutLinkKey, current buttonList: ' + str(buttonList))
        return None

    blockid = utils.getDataBetween(buttonList[0], 'blockid="', '"')

    return blockid

def getBetButton(htmlData, betInfo, betCommandLine):
    def rev(_bool):
        if betInfo['reverse']:
            return not _bool
        else:
            return _bool

    global g_handicaps, g_totals

    g_handicaps = []
    g_totals = []

    reverse = False
    firstMemberNumber = utils.getDataBetween(htmlData, 'member-number', '</b>',
                                             startOffset=2, jumps=['data-has-additional-markets'])
    if firstMemberNumber is None:
        utils.log('cant parse first member number')
        return None
    if firstMemberNumber[0] == '2':
        reverse = True

    eventTypeNumber = utils.getDataBetween(htmlData, 'shortcutLink_event', 'type')
    betButtonList = utils.getDataBetween(htmlData, '<td', '</td>', array=True)
    filterList = ['data-selection-price', 'data-selection-key']
    for filter in filterList:
        betButtonList = [x for x in betButtonList if filter in x]

    betCommandLine['contentData'].append({'recipient': 'tab', 'command': 'couponClick', 'commandData': []})
    commandCount = len(betCommandLine['contentData'])
    coef = 0.00
    for betButton in betButtonList:
        key = utils.getDataBetween(betButton, '@', '"', jumps=['data-selection-key'])
        coef = utils.getDataBetween(betButton, '"', '"', jumps=['data-selection-price'])
        coef = utils.toFloat(coef)
        if coef is None:
            utils.log('cant convert coef to float, coef: ' + str(coef))
            coef = 0.00
            continue

        # utils.log(betButton)

        if 'Asian' in key:
            continue
        if 'Minutes' in key:
            continue
        if 'Min' in key:
            continue
        if 'Corners' in key:
            continue
        if 'Cards' in key:
            continue
        if 'After' in key:
            continue
        if 'Lowest' in key:
            continue
        if 'Строго' in betButton:
            continue

        if betInfo['win']:
            if betInfo['win-type'] == 'normal-time':
                if not ('Match_Result' in key or 'Normal_Time_Result' in key):
                    if not ('Result.1' == key or 'Result.3' == key):
                        continue
                if rev(betInfo['team'] == 1) and '1' in key:
                    betCommandLine['contentData'][commandCount - 1]['commandData'].append(key)
                    break
                if rev(betInfo['team'] == 2) and '3' in key:
                    betCommandLine['contentData'][commandCount - 1]['commandData'].append(key)
                    break
            elif betInfo['win-type'] == 'total-win':
                if 'To_Qualify' not in key:
                    continue
                if rev(betInfo['team'] == 1) and 'home' in key:
                    betCommandLine['contentData'][commandCount - 1]['commandData'].append(key)
                    break
                if rev(betInfo['team'] == 2) and 'away' in key:
                    betCommandLine['contentData'][commandCount - 1]['commandData'].append(key)
                    break
        elif betInfo['draw']:
            if key == 'Match_Result.draw':
                betCommandLine['contentData'][commandCount - 1]['commandData'].append(key)
                break
        elif betInfo['win-draw']:
            if not ('Result.' in key or 'Result0.' in key):
                continue
            v1 = (('HB_H' in key and rev(betInfo['team'] == 1)) or ('HB_A' in key and rev(betInfo['team'] == 2)))
            v2 = (('HD' in key and (rev(betInfo['team'] == 1))) or ('AD' in key and rev(betInfo['team'] == 2)))
            if not (v1 or v2):
                continue
            betCommandLine['contentData'][commandCount - 1]['commandData'].append(key)
            break
        elif betInfo['win-win']:
            if key == 'Result.HA':
                betCommandLine['contentData'][commandCount - 1]['commandData'].append(key)
                break
        elif betInfo['win-handicap']:
            _key = key
            if not ('Handicap' in key or 'Draw_No_Bet' in key):
                continue
            _teamInKeyIs_1 = 'HB_H' in key
            _teamInKeyIs_2 = 'HB_A' in key
            _teamInBetIs_1 = rev(betInfo['team'] == 1)
            _teamInBetIs_2 = rev(betInfo['team'] == 2)
            if not (('HB_H' in key and rev(betInfo['team'] == 1)) or ('HB_A' in key and rev(betInfo['team'] == 2))):
                continue
            if betInfo['handicap-type'] is not None and betInfo['handicap-type'] not in betButton:
                continue
            if betInfo['part'] is not None and not ('Half' in key or 'Set' in key or 'Period' in key):
                continue
            # что бы проти дальше part долждна быть, и должна быть часть в ключе

            if betInfo['part'] is not None:
                if not ((betInfo['part'] == 1 and '1st' in key) or (betInfo['part'] == 2 and '1nd' in key)):
                    continue
            else:
                if '1st' in key or '2nd' in key or '3rd' in key or '4th' in key:
                    continue

            handicapText = None
            if 'coeff-handicap' in betButton:
                handicapText = utils.getDataBetween(betButton, '>', '<', jumps=['coeff-handicap'])
            elif 'data-market-type' in betButton:
                handicapText = utils.getDataBetween(betButton, '>', '<', jumps=['data-market-type'])
            else:
                continue
            if handicapText is None:
                utils.log('cant get handicap from text, text: ' + str(betButton))
                continue
            handicapText = handicapText.strip('( )\n<">')
            handicapFloat = utils.toFloat(handicapText)
            if handicapFloat is None:
                utils.log('cant convert handicap to float, handicap: ' + str(handicapText))
                continue
            #if handicapFloat != betInfo['handicap']:

            g_handicaps.append({'handicap': handicapFloat, 'coef': coef, 'keys': [key, handicapText]})
        elif betInfo['total-points']:
            if 'Total_' not in key:
                continue
            if betInfo['total-points-direction'] == 'under' and 'Under' not in key:
                continue
            if betInfo['total-points-direction'] == 'over' and 'Over' not in key:
                continue
            if betInfo['total-points-type'] is not None and betInfo['total-points-type'] not in betButton:
                continue
            if betInfo['team'] is not None:
                if not (('First' in key and rev(betInfo['team'] == 1)) or ('Second' in key and rev(betInfo['team'] == 2))):
                    continue
            else:
                if '_Team' in key:
                    continue
            if '1st' in key or '2nd' in key or '3rd' in key or '4th' in key:
                continue
            if 'Quarter' in key:
                continue

            pointsText = None
            if 'coeff-handicap' in betButton:
                pointsText = utils.getDataBetween(betButton, '>', '<', jumps=['coeff-handicap'])
            elif 'data-market-type' in betButton:
                pointsText = utils.getDataBetween(betButton, '>', '<', jumps=['data-market-type'])
            else:
                continue
            if pointsText is None:
                utils.log('cant get points from text, text: ' + str(betButton))
                continue
            pointsText = pointsText.strip(' )(\n<">')
            pointsFloat = utils.toFloat(pointsText)
            if pointsFloat is None:
                utils.log('cant convert points to float, points: ' + str(pointsText))
                continue

            g_totals.append({'total': pointsFloat, 'dir': betInfo['total-points-direction'],
                             'coef': coef, 'keys': [key, pointsText]})
    if betInfo['win-handicap']:
        betterHandicap = chooseBetterHandicap(betInfo)
        if betterHandicap is None:
            utils.log('cant find correct handicap, handicaps: ' + str(g_handicaps))
            return None
        if betInfo['part'] is not None:
            pass
            # betCommandLine['contentData'].insert(commandCount - 1, {'command': 'elementContainClick',
            #    'commandData': ['shortcut', 'shortcutLink_event' + eventTypeNumber + 'type10']})
        else:
            pass
            # betCommandLine['contentData'].insert(commandCount - 1, {'command': 'elementContainClick',
            #     'commandData': ['shortcut', 'shortcutLink_event' + eventTypeNumber + 'type2']})
        for key in betterHandicap['keys']:
            betCommandLine['contentData'][commandCount-1]['commandData'].append(key)
    elif betInfo['total-points']:
        betterTotal = chooseBetterTotal(betInfo)
        if betterTotal is None:
            utils.log('cant find correct total, totals: ' + str(g_totals))
            return None
        # betCommandLine['contentData'].insert(commandCount - 1, {'command': 'elementContainClick',
        #     'commandData': ['shortcut', 'shortcutLink_event' + eventTypeNumber + 'type3']})
        for key in betterTotal['keys']:
            betCommandLine['contentData'][commandCount-1]['commandData'].append(key)
    else:
        # is all right there!!!
        if not utils.compareNumber(betInfo['coef'], currentCoef=coef):
            utils.log('bad coef, target coef: ' + str(betInfo['coef']) + ', current coef: ' + str(coef))
            return None

    if len(betCommandLine['contentData'][commandCount - 1]['commandData']) <= 0:
        utils.log('commandData is empty')
        return None

    return betCommandLine

def getGameUrl(sportTypeUrl, gameName, targetDate):
    request = None
    try:
        request = requests.get(sportTypeUrl)
    except:
        utils.log('[BK.MARATHONBET] Error, requests.get() raise exception')
        return None
    htmlData = request.text

    #utils.log('htmlData: ' + str(htmlData))

    #gameNameWordCount = len(gameName.split())

    curUrl = None
    curName = None
    percMax = 0

    gameNameViriants = [gameName, gameName.replace(" - ", " @ ")]
    exactMatch = gameNameViriants[0] in htmlData or gameNameViriants[1] in htmlData
    if exactMatch:
        for gameNameViriant in gameNameViriants:
                startIndex = htmlData.index(gameNameViriant) if gameNameViriant in htmlData else None
                if startIndex is not None:
                    htmlData = htmlData[startIndex:]
                    url = utils.getDataBetween(htmlData, 'data-event-page="', '">')
                    if url is not None:
                        curUrl = url
                        break
    else:
        gameName = utils.stringCutBrackerts(gameName)
        gameName = utils.stringGarbageClear(gameName)

        currentDate = datetime.datetime.now()
        targetDate = datetime.datetime.strptime(targetDate, '%d-%m %H:%M')
        targetDate = targetDate.replace(year=currentDate.year)
        # if targetDate - currentDate > 300 days = + year

        eventList = utils.getDataBetween(htmlData, 'data-event-treeId', '</tbody>', array=True)
        utils.log('gameName in prognoz : ' + str(gameName))
        for event in eventList:
            date = utils.getDataBetween(event, '>', '<', jumps=['date'])
            date = date.strip('( )\n<">')
            dateParts = date.split(' ')

            dateCoef = 0
            delta = None
            gameDate = currentDate
            if len(date) >= 5:
                if len(dateParts) == 1:
                    gameDate = datetime.datetime.strptime(date, '%H:%M')
                    gameDate = gameDate.replace(year=currentDate.year, month=currentDate.month, day=currentDate.day)
                if len(dateParts) == 3:
                    replaceArray = [['авг', '08'], ['сен', '09'], ['окт', '10']]
                    for month in replaceArray:
                        date = date.replace(month[0], month[1])
                    gameDate = datetime.datetime.strptime(date, '%d %m %H:%M')
                    gameDate = gameDate.replace(year=currentDate.year)
                if len(dateParts) == 1 or len(dateParts) == 3:
                    delta = abs(targetDate - gameDate)
                    deltaMin = delta.total_seconds() / 60
                    if deltaMin == 0:
                        dateCoef = 20
                    elif deltaMin <= 5:
                        dateCoef = 10

            name = utils.getDataBetween(event, '"', '"', jumps=['data-event-name'])
            name = utils.stringCutBrackerts(name)
            name = utils.stringGarbageClear(name)
            #if gameNameWordCount == 1:
            #    name = name.split()[0]
            perc = utils.search_partial_text(gameName, name) + dateCoef
            utils.log('gameName in array : ' + str(name) + ',    perc: ' + str(perc) +
                      ',  delta: ' + str(delta) + ', dateCoef: ' + str(dateCoef))
            if perc > 80 and perc > percMax:
                percMax = perc
                curUrl = utils.getDataBetween(event, 'data-event-page="', '"')
                curName = name
                if perc >= 100:
                    break

    utils.log('better match game name: ' + str(curName) + ', perc: ' + str(percMax) + ', game url: ' + str(curUrl))
    reverse = False

    if not exactMatch and curName is not None:
        curName = curName.replace(" @ ", " - ")
        curNameParts = curName.split(' - ')
        gameNameParts = gameName.split(' - ')
        v1 = utils.search_partial_text(gameNameParts[0], curNameParts[0])
        v1 = v1 + utils.search_partial_text(gameNameParts[1], curNameParts[1])
        v2 = utils.search_partial_text(gameNameParts[0], curNameParts[1])
        v2 = v2 + utils.search_partial_text(gameNameParts[1], curNameParts[0])
        if v2 > v1:
            reverse = True

    if not exactMatch and curUrl is None:
        return None, reverse

    if not exactMatch:
        utils.log('better match name: ' + curName + ', perc : ' + str(percMax))

    return g_marathonUrl[:-1] + curUrl, reverse

def getBetCommandLine(bet):
    sportTypeUrl = None
    for _sportTypeUrl in g_sportTypeUrlList:
        if _sportTypeUrl['sportType'] == bet['sportType']:
            sportTypeUrl = _sportTypeUrl['url']

    if sportTypeUrl is None:
        utils.log('[MARATHON] unknown sport type: ' + bet['sportType'])
        return None

    gameUrl, reverse = getGameUrl(sportTypeUrl, bet['gameName'], bet['gameDate'])
    if gameUrl is None:
        utils.log('[MARATHON] cant get game url: ' + str(bet['gameName']))
        return None
    bet['betInfo']['reverse'] = reverse

    betCommandLine = {'contentType': 'commandList', 'contentData': []}
    betCommandLine['contentData'].append({'recipient': 'ext', 'command': 'openUrl', 'commandData': gameUrl})
    #tab

    htmlData = requests.get(gameUrl).text
    betCommandLine = getBetButton(htmlData, bet['betInfo'], betCommandLine)
    if betCommandLine is None:
        utils.log('cant find correct bet getBetButton, url: ' + str(gameUrl))
        return None

    return betCommandLine

def getAllSports():
    global g_sportTypeUrlList

    htmlData = requests.get(g_marathonUrl + 'su/').text
    htmlData = utils.getDataBetween(htmlData, 'reactData = ', '}}};', endOffset=3)

    sportsJSON = json.loads(htmlData)
    sports = sportsJSON['prematchLeftPanel']['regularMenu']['childs']
    for sport in sports:
        g_sportTypeUrlList.append({'sportType': sport['label'], 'url': g_marathonUrl[:-1] + sport['href']})

def init():
    def _itit():
        utils.log('bk.marathonbet start')
        getAllSports()
    threading.Thread(target=_itit, name='bk.marathonbet').start()