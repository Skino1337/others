import threading
import time
import datetime

import requests

import utils

g_sportTypeIDList = {'Футбол': ['1', 'soccer'], 'Теннис': ['2', 'tennis'], 'Баскетбол': ['3', 'basketball'],
                     'Волейбол': ['12', 'volleyball'], 'Настольный теннис': ['46', 'table-tennis']}

def getEventUrl(sportType, eventName, eventDate=None):
    if sportType not in g_sportTypeIDList:
        utils.log('[BK.BETCITY] (getEventUrl) Error, unknown sport type: ' + str(sportType))
        return None
    sportTypeID = g_sportTypeIDList[sportType][0]
    sportTypeName = g_sportTypeIDList[sportType][1]
    eventNameOriginal = eventName
    eventName = eventName.lower()
    eventName = utils.stringCutBrackerts(eventName)
    eventName = utils.stringGarbageClear(eventName)
    eventName = eventName.replace('/', ' ')
    eventName = eventName.replace('.', ' ')
    eventNamePartList = eventName.split()
    eventNamePartList = [i for i in eventNamePartList if len(i) > 3]
    eventNamePartList = sorted(eventNamePartList, key=lambda i: len(i))
    eventNameUnited = ''
    for eventNamePart in eventNamePartList:
        eventNameUnited = eventNameUnited + eventNamePart

    utils.log('[BK.BETCITY] (getEventUrl) Info, event name original: ' + str(eventNameOriginal))
    utils.log('[BK.BETCITY] (getEventUrl) Info, event name parts: ' + str(eventNamePartList))

    resultUrl = None
    resultName = None
    for eventNamePart in eventNamePartList:
        request = None
        try:
            request = requests.get('https://ad.betcity.ru/d/search?txt=' + eventNamePart + '&is_line=1')
        except:
            utils.log('[BK.BETCITY] (getEventUrl) Error, requests.get(search) raise exception')
            return None

        jsonData = None
        try:
            jsonData = request.json()
        except:
            utils.log('[BK.BETCITY] (getEventUrl) Error, no json object could be decoded: ' + str(request.text))
            return None

        jsonEventList = jsonData
        jsonEventList = jsonEventList['reply'] if 'reply' in jsonEventList else {}
        if 'result' not in jsonEventList:
            time.sleep(0.1)
            continue
        jsonEventList = jsonEventList['result']
        jsonEventList = jsonEventList['OFFLINE'] if 'OFFLINE' in jsonEventList else {}
        jsonEventList = jsonEventList[sportTypeID] if sportTypeID in jsonEventList else {}

        eventList = []
        if 'chmps' in jsonEventList:
            for chmp in jsonEventList['chmps']:
                chmp = jsonEventList['chmps'][chmp]
                if 'evts' in chmp:
                    for evt in chmp['evts']:
                        evt = chmp['evts'][evt]
                        sp = sportTypeName
                        ch = str(evt['id_ch'])
                        ev = str(evt['id_ev'])
                        eventList.append({'name': evt['name_ev'], 'date': evt['date_ev_str'],
                                          'url': 'https://betcity.ru/ru/line/' + sp + '/' + ch + '/' + ev})

        percMax = 0
        for event in eventList:
            deltaMin = 0
            if eventDate is not None:
                tDate = datetime.datetime.strptime(eventDate, '%Y-%m-%d %H:%M')
                eDate = datetime.datetime.strptime(event['date'], '%Y-%m-%d %H:%M')
                delta = abs(tDate - eDate)
                deltaMin = delta.total_seconds() / 60

            name = event['name']
            name = name.lower()
            name = utils.stringCutBrackerts(name)
            name = utils.stringGarbageClear(name)
            name = name.replace('/', ' ')
            name = name.replace('.', ' ')
            namePartList = name.split()
            namePartList = [i for i in namePartList if len(i) > 3]
            namePartList = sorted(namePartList, key=lambda i: len(i))
            nameUnited = ''
            for namePart in namePartList:
                nameUnited = nameUnited + namePart

            perc = utils.search_partial_text(eventNameUnited, nameUnited)
            utils.log('[BK.BETCITY] (getEventUrl) Info, cmp name: (' + eventNameUnited + '==' + nameUnited
                      + '), percent match: ' + str(perc) + '>80>70')
            utils.log('[BK.BETCITY] (getEventUrl) Info, cmp date: (' + str(eventDate) + '==' + str(event['date'])
                      + '), delta min: ' + str(deltaMin) + '<55')

            if perc >= 80:
                percMax = perc
                resultUrl = event['url']
                resultName = name
                break

            if perc >= 70 and perc > percMax:
                if deltaMin < 55:
                    percMax = perc
                    resultUrl = event['url']
                    resultName = name

        if resultUrl:
            break

        time.sleep(0.1)

    # TODO reverse

    if not resultUrl:
        utils.log('[BK.BETCITY] (getEventUrl) Info, no search result for words: ' + str(eventNamePartList))

    return resultUrl

def init():
    def _itit():
        utils.log('bk.betcity start')
        # url = getEventUrl('Теннис', 'Чоински Я. - Хорански Ф.', '2018-08-19 16:00')
        # utils.log('url: ' + str(url))
    threading.Thread(target=_itit, name='bk.betcity').start()

# init()
# time.sleep(1000)