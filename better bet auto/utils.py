import datetime

import win32file
import win32con

g_logFile = None


def log(data):
    global g_logFile

    data = str(data)

    if g_logFile is None:
        g_logFile = win32file.CreateFile('log.txt',
                                      win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                                      win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE,
                                      None,
                                      win32con.CREATE_ALWAYS,
                                      0,
                                      None)

    dateFormated = datetime.datetime.today().strftime('%H:%M:%S:%f')
    dateFormated = dateFormated[:12]
    data = '[' + dateFormated + '] ' + data

    dataBytesFile = (data + '\n').encode('utf8')
    win32file.WriteFile(g_logFile, dataBytesFile)
    print(data)

def dateFromTimestamp(i):
    date = datetime.datetime.fromtimestamp(i)
    return date.strftime('%d-%m %H:%M')

def getFullData(dataString):
    dateNew = datetime.datetime.strptime(dataString, '%d-%m %H:%M')
    dateNew = dateNew.replace(year=2018, second=0, microsecond=0)

    return dateNew.strftime('%Y-%m-%d %H:%M')

def checkRelevanceDate(tDate):
    if isinstance(tDate, str):
        tDate = datetime.datetime.strptime(tDate, '%d-%m %H:%M')
        tDate = tDate.replace(year=2018, second=0, microsecond=0)
    elif isinstance(tDate, int):
        tDate = datetime.datetime.fromtimestamp(tDate)
        tDate = tDate.replace(second=0, microsecond=0)
    tDate = tDate - datetime.timedelta(minutes=10)

    cDate = datetime.datetime.now()
    cDate = cDate.replace(second=0, microsecond=0)

    delta = tDate - cDate
    deltaSec = delta.total_seconds()

    if deltaSec > 0:
        return True

    return False

def search_partial_text(src, dst):
    dst_buf = dst
    result = 0
    for char in src:
        if char in dst_buf:
            dst_buf = dst_buf.replace(char, '', 1)
            result += 1
    r1 = int(result / len(src) * 100)
    r2 = int(result / len(dst) * 100)

    return r1 if r1 < r2 else r2

def stringCutBrackerts(string):
    while '(' in string and ')' in string:
        start = string.find('(')
        end = string.find(')')
        string = string.replace(string[start:end + 1], '')

    return string

def stringCutInitials(string):
    initialList = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    for initial in initialList:
        string = string.replace(initial + '.', '')

    return string

def stringGarbageClear(string, garbageList=None):
    if garbageList is None:
        garbageList = ['фк', 'до', '16', '(16)', '18', '(18)', '20', '(20)',
                       'жен', '(жен)', '(ж)', 'муж', '(муж)', '(м)']
    for garbage in garbageList:
            string = string.replace(garbage, '')

    # TODO element like a part of command name, хумоДОри

    return string

def getParsedData(data, startDataList, endDataList, array=False):
    resultList = []
    indexStart = 0
    loop = True
    while loop:
        for startData in startDataList:
            indexStart = data.find(startData, indexStart)
            if indexStart < 0:
                loop = False
            indexStart = indexStart + len(startData)

        if not loop:
            break

        indexEndLast = 0
        indexEnd = indexStart
        for endData in endDataList:
            indexEnd = data.find(endData, indexEnd)
            if indexEnd < 0:
                loop = False
            indexEndLast = indexEnd
            indexEnd = indexEnd + len(endData)

        resultList.append(data[indexStart:indexEndLast])

        if not array:
            break

    if len(resultList) <= 0:
        return None

    return resultList if array else resultList[0]

def getDataBetween(data, startData, endData, startOffset=0, endOffset=0, array=False, jumps=[]):
    for jump in jumps:
        startIndex = data.index(jump) if jump in data else None
        if startIndex is None:
            log('"' + jump + '" not in ' + data)
            return None
        data = data[startIndex + 1:]

    returnData = []
    while True:
        startIndex = data.index(startData) if startData in data else None
        if startIndex is None:
            if array:
                break
            else:
                log('startData: "' + startData + '" not in ' + data)
            return None
        try:
            data = data[startIndex + len(startData) + startOffset:]
        except:
            log('getDataBetween error, mb MemoryError MemoryError')
            return None

        endIndex = data.index(endData) if endData in data else None
        if endIndex is None:
            if array:
                break
            else:
                log('endData: "' + endData + '" not in ' + data)
            return None
        if not array:
            data = data[:endIndex + endOffset]
            break

        returnData.append(data[:endIndex + endOffset])

    if array:
        return returnData

    return data

def compareNumber(targetCoef, currentCoef=None, v=0.20):
    if currentCoef is None:
        currentCoef = targetCoef
    minTargetCoef = targetCoef - ((targetCoef - 1.00) * v)
    maxTargetCoef = targetCoef + ((targetCoef - 1.00) * v)
    return minTargetCoef < currentCoef < maxTargetCoef

def toFloat(value):
    if isinstance(value, float):
        return value
    try:
        value = float(value)
        return value
    except:
        return None