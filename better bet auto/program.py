import server
import utils
import time

import harvesters.vprognoze
import harvesters.prognozist
import harvesters.betonsuccess
import bk.marathonbet
import bet_manager

import asyncio
import discord_bot

import requests
import threading

testBet = {'gameName': 'Нью-Йорк Либерти - Финикс Меркьюри',
           'gameDate': '20-08 01:00',
           'sportType': 'Баскетбол',
           'bet': 'ТБ (165) @ 1.75',
           'betInfo': None}

def myCode():

    bk.marathonbet.init()

    time.sleep(4)

    betinfo = harvesters.vprognoze.parseBet(testBet)
    if betinfo is None:
        utils.log('parseBet() return None, bet: \n' + str(testBet))

    utils.log('betinfo: ' + str(betinfo))
    testBet['betInfo'] = betinfo

    betCommandLine = bk.marathonbet.getBetCommandLine(testBet)

    utils.log('betCommandLine: ' + str(betCommandLine))

    while not server.isBrowserReadyToBet():
        time.sleep(0.1)

    #server.send(betCommandLine)


# TODO
# preload maraphone
# better prognozist parser for oleg777
# TODO


if __name__ == '__main__':
    # utils.log('program start')
    # threading.Thread(target=myCode).start()

    utils.log('program start')

    server.init()
    harvesters.vprognoze.init()
    # harvesters.prognozist.init()
    # harvesters.betonsuccess.init()
    bk.marathonbet.init()
    bet_manager.init()
    #discord_bot.init()


    # testBet['betInfo'] = harvesters.vprognoze.parseBet(testBet)
    #
    # betCommandLine = {'contentType': 'commandLine', 'contentData': []}
    #
    # htmlData = requests.get('https://www.marathonbet.ru/su/betting/Basketball/WNBA/New+York+Liberty+%40+Phoenix+Mercury+-+7152942/').text
    #
    # betCommandLine = bk.marathonbet.getBetButton(htmlData, testBet['betInfo'], betCommandLine)
    # utils.log(betCommandLine)


    # bk.marathonbet.getGameUrl('https://www.marathonbet.ru/su/betting/Football/?menu=11',
    #                           'Дуйсбург - Бохум', '11-08 14:00')

    # server.init()
    #
    # while not server.isBrowserReadyToBet():
    #     time.sleep(0.1)
    #
    # utils.log('server send')
    #
    # url = 'https://www.marathonbet.ru/su/betting/Football/Russia/Premier+League/Rostov+vs+Rubin+Kazan+-+7020425/'
    # server.send({'contentType': 'commandList', 'contentData': [
    #     {'recipient': 'ext', 'command': 'openUrl', 'commandData': url},
    #     {'recipient': 'tab', 'command': 'couponClick', 'commandData': ['Match_Result.1']},
    #     {'recipient': 'tab', 'command': 'typeText', 'commandData': '5 perc'}]})


    # betInfo = harvesters.vprognoze.parseBet(testBet)
    # testBet['betInfo'] = betInfo
    #
    # betCommandLine = {'contentType': 'commandLine', 'contentData': []}
    #
    # htmlData = requests.get('https://www.marathonbet.ru/su/betting/Ice+Hockey/Friendlies/Clubs/Ak+Bars+vs+Lokomotiv+-+7129261/').text
    #
    # betCommandLine = bk.marathonbet.getBetButton(htmlData, testBet['betInfo'], betCommandLine)
    # if betCommandLine is None:
    #     utils.log('FAIL')


    #threading.Thread(target=myCode).start()

    #bk.marathonbet.getGameUrl('https://www.marathonbet.ru/su/betting/Football/?menu=11', 'Хаммарбю - Треллеборг')

    #betInfo = harvesters.vprognoze.parseBet(testBet)
    #testBet['betInfo'] = betInfo

    #utils.log(testBet)

    # server.init()

    #bk.marathonbet.g_sportTypeUrlList.append({'sportType': 'Футбол',
    #                                          'url': 'https://www.marathonbet.ru/su/betting/Football/?menu=11'})

    #commandLine = bk.marathonbet.getBetCommandLine(testBet)

    #utils.log(commandLine)

    # while not server.isBrowserReadyToBet():
    #     time.sleep(0.1)
    #
    # utils.log('server pre send')
    #
    # server.send({'contentType': 'commandLine', 'contentData': [
    #     {'command': 'openUrl', 'commandData': 'https://www.marathonbet.ru/su/betting/Football/Clubs.+International/UEFA+Super+Cup/Tallinn/Real+Madrid+vs+Atletico+Madrid+-+6879624/'},
    #     {'command': 'elementContainClick', 'commandData': ['shortcut', 'shortcutLink_event6879624type2']},
    #     {'command': 'elementContainClick', 'commandData': ['coupon', 'To_Win_Match_With_Handicap1.HB_H', '-1.5']}]})
    #
    # utils.log('server post send')

    #
    # utils.log('program run')
    #
    # server.init()
    #
    # while not server.isBrowserReadyToBet():
    #     time.sleep(0.1)
    #
    # utils.log('program send betCommandLine')
    #
    # betCommandLine = {'contentType': 'commandLine', 'contentData': []}
    # betCommandLine['contentData'].append({'command': 'openUrl', 'commandExec': 'ext',
    #     'commandData': 'https://www.marathonbet.ru/su/betting/Football/England/Premier+League/Manchester+United+vs+Leicester+City+-+6938900/'})
    #
    # betCommandLine['contentData'].append({'command': 'elementContainClick', 'commandExec': 'ext',
    #                                       'commandData': ['coupon', 'Match_Result.1']})
    #
    # betCommandLine['contentData'].append({'command': 'dialText', 'commandExec': 'ext',
    #                                       'commandData': '10 perc'})
    # #
    # # betCommandLine['contentData'].append({'command': 'elementContainClick', 'commandExec': 'ext',
    # #                                       'commandData': ['dealBetButton']})
    #
    # server.send(betCommandLine)
    #
    # utils.log('program end')
    #


    #htmlData = requests.get('https://www.marathonbet.ru/su/betting/Football/England/Premier+League/Manchester+United+vs+Leicester+City+-+6938900/').text
    #bk.marathonbet.parseGamePage(htmlData)
    #bk.marathonbet.init()
    #harvesters.vprognoze.init()
    #server.init()
    #utils.log('program end')

    #readyBetListChecker()

    #utils.log('program close')