import threading
import json
import utils
import pyautogui
import time
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket

g_socket = None
g_isBrowserReadyToBet = False
g_isWaitResponse = False
g_isBrowserConnected = False

def test():
    return
    send(
        {
            'contentType': 'commandList', 'contentData':
            [
                {'recipient': 'ext', 'command': 'openUrl',
                 'commandData': 'https://www.marathonbet.ru/su/betting/Football/Internationals/UEFA+Nations+League/League+A/Group+Stage/Germany+vs+France+-+6405779/'},
                {'recipient': 'tab', 'command': 'couponClick', 'commandData': ['Match_Result.1']},
                #{'recipient': 'tab', 'command': 'dealBet', 'commandData': ''}
            ]
        })

def clickMousePosition(x, y):
    pyautogui.moveTo(x, y, 0.5)
    time.sleep(0.5)
    pyautogui.click()

def scrollMouseWheel(dir, times):
    rev = 1
    if dir == 'down':
        rev = -1
    for i in range(0, times):
        pyautogui.scroll(100*rev, pause=0.5)

def dialText(text):
    pyautogui.typewrite(text, interval=0.5)

def isBrowserReadyToBet():
    return g_isBrowserReadyToBet and g_isBrowserConnected and not g_isWaitResponse

def onMessage(data):
    global g_isBrowserReadyToBet, g_isWaitResponse

    jsonData = json.loads(data)

    if jsonData['contentType'] == 'commandLine':
        commandList = jsonData['contentData']
        for command in commandList:
            utils.log('[Server] got command: ' + str(command))
            if command['command'] == 'updateReady':
                g_isWaitResponse = False
                if command['commandData'] == 'true':
                    g_isBrowserReadyToBet = True
                    test()
                elif command['commandData'] == 'false':
                    g_isBrowserReadyToBet = False
                else:
                    utils.log('[Server] cant recognize browser command: ' + str(command))
            elif command['command'] == 'clickMousePosition':
                x = command['commandData']['x']
                y = command['commandData']['y']
                clickMousePosition(x, y)
                betCommandLine = {'contentType': 'commandResult', 'contentData': 'elementContainClick' + '=true'}
                send(betCommandLine)
            elif command['command'] == 'scrollMouseWheel':
                dir = command['commandData']['dir']
                times = command['commandData']['times']
                scrollMouseWheel(dir, times)
                betCommandLine = {'contentType': 'commandResult', 'contentData': 'scrollMouseWheel' + '=true'}
                send(betCommandLine)
            elif command['command'] == 'dialText':
                text = command['commandData']
                dialText(str(text))
                betCommandLine = {'contentType': 'commandResult', 'contentData': 'dialText' + '=true'}
                send(betCommandLine)

def onConnect(address):
    global g_isBrowserConnected

    g_isBrowserConnected = True
    utils.log('[Server] onConnect: ' + str(address))

def onClose():
    global g_isBrowserConnected

    g_isBrowserConnected = False
    utils.log('[Server] onDisconnect')

def send(data):
    if type(data) is dict:
        data = json.dumps(data)
    else:
        data = str(data)
    g_socket.sendMessage(data)

class wsServer(WebSocket):

    def handleMessage(self):
        threading.Thread(target=onMessage, args=[self.data]).start()

    def handleConnected(self):
        global g_socket

        g_socket = self
        threading.Thread(target=onConnect, args=[self.address]).start()

    def handleClose(self):
        threading.Thread(target=onClose).start()

def init():
    def _init():
        global g_socket

        g_socket = wsServer
        server = SimpleWebSocketServer('', 8000, g_socket)
        server.serveforever()

    utils.log('server start')
    threading.Thread(target=_init, name='harvesters.vprognoze').start()