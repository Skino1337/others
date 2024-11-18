from time import sleep
import random
from ctypes import wintypes, windll
import threading

import win32gui
import win32process
import win32con
import psutil
import pyautogui
import keyboard
import pyperclip

import pywinauto

game_process_name = 'PathOfExile'
game_window_name = 'Path of Exile'


def get_game_processid_list():
    processid_list = []
    for process in psutil.process_iter(['name']):
        if game_process_name in process.info['name']:
            processid_list.append(process.pid)

    return processid_list


def get_game_processid_and_hwnd():
    pid_list = get_game_processid_list()
    game_processid = None
    game_hwnd = None

    def enum_window_callback(hwnd, _):
        nonlocal game_processid, game_hwnd
        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
            threadid, processid = win32process.GetWindowThreadProcessId(hwnd)
            if processid in pid_list and game_window_name in win32gui.GetWindowText(hwnd):
                game_processid = processid
                game_hwnd = hwnd

    win32gui.EnumWindows(enum_window_callback, None)

    return game_processid, game_hwnd


def is_game_active():
    hwnd_active = windll.user32.GetForegroundWindow()
    pid_game, hwnd_game = get_game_processid_and_hwnd()

    return hwnd_game == hwnd_active


def activate_game_window():
    if is_game_active():
        return True

    pid_game, hwnd_game = get_game_processid_and_hwnd()

    app = pywinauto.application.Application()
    window = app.window_(handle=hwnd_game)

    if hwnd_game:
        for i in range(0, 3):
            '''
            https://docs.microsoft.com/ru-ru/windows/win32/api/winuser/nf-winuser-showwindow?redirectedfrom=MSDN
            https://stackoverflow.com/questions/2090464/python-window-activation
            '''

            window.SetFocus()


            '''
            pid_current = threading.get_ident()

            win32process.AttachThreadInput(hwnd_game, pid_current, True)
            windll.user32.BringWindowToTop(hwnd_game)
            windll.user32.ShowWindow(hwnd_game, 5)
            win32process.AttachThreadInput(hwnd_game, pid_current, False)

            
            windll.user32.BringWindowToTop(hwnd_game)
            windll.user32.SetForegroundWindow(hwnd_game)
            windll.user32.ShowWindow(hwnd_game, 5)
            
            
            win32gui.SetForegroundWindow(hwnd_game)
            win32gui.ShowWindow(hwnd_game, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd_game)
            win32gui.ShowWindow(hwnd_game, win32con.SW_RESTORE)
            '''

            if is_game_active():
                return True

            sleep(0.05)

    return False


def write_copypaste_text(data):
    if activate_game_window():
        pyperclip.copy(data)

        keyboard.press_and_release('enter')

        sleep(random.uniform(10, 20) / 1000)
        keyboard.press('ctrl')
        sleep(random.uniform(10, 20) / 1000)
        keyboard.press_and_release('v')
        sleep(random.uniform(10, 20) / 1000)
        keyboard.release('ctrl')
        sleep(random.uniform(10, 20) / 1000)

        keyboard.press_and_release('enter')


def get_game_screen():
    pid_game, hwnd_game = get_game_processid_and_hwnd()
    image = None
    if hwnd_game:
        x, y, x1, y1 = win32gui.GetClientRect(hwnd_game)
        x, y = win32gui.ClientToScreen(hwnd_game, (x, y))
        x1, y1 = win32gui.ClientToScreen(hwnd_game, (x1 - x, y1 - y))
        image = pyautogui.screenshot(region=(x, y, x1, y1))

    return image
