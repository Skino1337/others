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

gameName = 'Арлан - Алтай-Торпедо'
curName = 'Арлан Кокшетау - Алтай Торпе'

curName = curName.replace(" @ ", " - ")
curNameParts = curName.split(' - ')
gameNameParts = gameName.split(' - ')
v1 = search_partial_text(gameNameParts[0], curNameParts[0])
v1 = v1 + search_partial_text(gameNameParts[1], curNameParts[1])
v2 = search_partial_text(gameNameParts[0], curNameParts[1])
v2 = v2 + search_partial_text(gameNameParts[1], curNameParts[0])
if v2 > v1:
    reverse = True