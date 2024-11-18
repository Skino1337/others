def parse(betResult):
    betInfo = {}

    if 'проход дальше' in betResult:
        if '1-я' in betResult:
            betInfo['team'] = 1
        elif '2-я' in betResult:
            betInfo['team'] = 2
        betInfo['win'] = True
        betInfo['win-type'] = 'total-win'
        return betInfo, None
    elif 'п1' == betResult or 'п2' == betResult:
        if '1' in betResult:
            betInfo['team'] = 1
        elif '2' in betResult:
            betInfo['team'] = 2
        betInfo['win'] = True
        betInfo['win-type'] = 'main-time'
        return betInfo, None
    elif betResult == 'ничья':
        betInfo['draw'] = True
        return betInfo, None
    elif 'двойной шанс' in betResult:
        if '1' in betResult:
            betInfo['team'] = 1
        elif '2' in betResult:
            betInfo['team'] = 2
        betInfo['win-draw'] = True
        return betInfo, None
    else:
        return None, ('cant parse bet result, bet result: ' + str(betResult))