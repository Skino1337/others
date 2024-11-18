import threading
import time

import utils
import server
import bk.marathonbet
import bk.betcity

import asyncio
import discord_bot

g_readyBetList = []

def addBet(bet):
    global g_readyBetList
    lenght = len(g_readyBetList)
    utils.log('g_readyBetList lenght is: ' + str(lenght))

    g_readyBetList[lenght-1] = bet

def makeBet():
    global g_readyBetList

    bet = g_readyBetList[0]
    g_readyBetList.pop(0)

    betCommandLine = bk.marathonbet.getBetCommandLine(bet)
    if betCommandLine:
        betCommandLine['contentData'].append({'recipient': 'tab', 'command': 'typeText', 'commandData': '5 perc'})
        betCommandLine['contentData'].append({'recipient': 'tab', 'command': 'dealBet', 'commandData': ['dealBet']})

        server.send(betCommandLine)
        server.g_isWaitResponse = True

        utils.log('DO BET: ' + str(bet) + ' ' + str(betCommandLine))
    else:
        if server.g_isBrowserConnected:
            discord_bot.discordWriteMessage('Cant do bet:' + '\n'
                                            + 'sources: ' + bet['sources'] + '\n'
                                            + 'gameName: ' + bet['gameName'] + '\n'
                                            + 'bet: ' + bet['bet'])
        utils.log('cant get betCommandLine, bet: ' + str(bet))
        date = utils.getFullData(bet['gameDate'])
        url = bk.betcity.getEventUrl(bet['sportType'], bet['gameName'], date)
        if url:
            utils.log('try betcity : ' + str(url))

def checkReadyBetLoop():
    while True:
        time.sleep(0.1)

        if len(g_readyBetList) <= 0:
            continue

        if not server.isBrowserReadyToBet():
            continue

        makeBet()

def init():
    utils.log('bet_manager start')
    threading.Thread(target=checkReadyBetLoop, name='bet_manager').start()