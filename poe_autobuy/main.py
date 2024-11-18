from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By

import keyboard

import random
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from threading import Thread
from time import sleep
import json

import game_interact

config_json = None
buy_message_list = []
spam_list = []


def add_message_to_buy_list(message):
    player_name = message.split()[0]
    if player_name not in spam_list:
        spam_list.append(player_name)
        print('add to spam list: ' + str(player_name))
        buy_message_list.append(message)


def message_manager():
    global buy_message_list
    while True:
        sleep(0.1)

        if len(buy_message_list) < 1:
            continue
        if not game_interact.is_game_active():
            continue
        if keyboard.is_pressed('alt'):
            continue
        if keyboard.is_pressed('shift'):
            continue
        if keyboard.is_pressed('ctrl'):
            continue

        game_interact.write_copypaste_text(buy_message_list[0])
        buy_message_list.pop(0)
        sleep(1)


def read_config():
    global config_json
    config_file = open('config.txt', 'r')
    config_json = json.load(config_file)


class SimpleEcho(WebSocket):
    def handleMessage(self):
        global buy_message_list
        # print(self.data)
        data_json = json.loads(self.data)
        # print(data_json)
        if 'message_type' in data_json and data_json['message_type'] == 'trade':
            if 'message_data' in data_json and data_json['message_data']:
                print(data_json['message_data']['copy_text'])
                add_message_to_buy_list(data_json['message_data']['copy_text'])

    def handleConnected(self):
        print(self.address, 'connected')

    def handleClose(self):
        print(self.address, 'closed')


def websocket():
    server = SimpleWebSocketServer('', 8000, SimpleEcho)
    server.serveforever()


def run_selenium():
    js_file_data = open('poe_autobuy_inject.js', 'r').read()

    options = webdriver.FirefoxOptions()

    if config_json['headless'] == 'y':
        options.add_argument('-headless')

    driver = webdriver.Firefox(options=options)
    wait = WebDriverWait(driver, 10)
    # driver.set_window_rect(10, 10, 1000, 800)
    driver.maximize_window()

    sleep(2)

    elem = []
    driver.get('https://www.pathofexile.com/trade/search/' + config_json['league'] + '/')
    print('driver.load_initial_page')
    while len(elem) == 0:
        elem = driver.find_elements(By.CLASS_NAME, 'search-btn')
        sleep(0.1)

    driver.delete_all_cookies()
    print("driver.delete_all_cookies")
    sleep(1)

    driver.add_cookie({'name': 'POESESSID', 'value': config_json['POESESSID']})
    print("driver.add_cookies")
    sleep(1)

    elem = []
    driver.refresh()
    print("driver.refresh")
    while len(elem) == 0:
        elem = driver.find_elements(By.CLASS_NAME, 'search-btn')
        sleep(0.1)

    for item in config_json['items']:
        if item['disable'] == 'y':
            continue

        old_windows = driver.window_handles

        driver.execute_script('window.open("");')
        print("driver.create_new_tab")
        sleep(2)

        wait.until(ec.new_window_is_opened(old_windows))
        new_window = [i for i in driver.window_handles if i not in old_windows]
        driver.switch_to.window(new_window[0])
        print("driver.switch_to_new_tab")
        sleep(1)

        elem = []
        driver.get('https://www.pathofexile.com/trade/search/' + config_json['league'] + '/' + item['code'] + '/live')
        print('driver.get_url(' + item['code'] + ')')
        while len(elem) == 0:
            elem = driver.find_elements(By.CLASS_NAME, 'livesearch-btn')
            sleep(0.1)

        driver.execute_script('document.title = "' + item['description'] + '"')
        print('driver.change_window_title')
        sleep(2)

        driver.execute_script(js_file_data)
        print('driver.execute_js')
        sleep(2)


def main():
    read_config()

    '''
    game_interact.activate_game_window()
    image = game_interact.get_game_screen()
    if image:
        image.show()
    '''

    thread_websocket = Thread(target=websocket).start()
    thread_selenium = Thread(target=run_selenium).start()
    thread_message_manager = Thread(target=message_manager).start()


main()
