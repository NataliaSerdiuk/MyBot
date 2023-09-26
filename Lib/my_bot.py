from token_to import *
from vk_api.longpoll import VkLongPoll, VkEventType
from transliterate import translit
from button import *
import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import NoSuchElementException, TimeoutException

vk = vk_api.VkApi(token=vk_token)
longpoll = VkLongPoll(vk)
vk_id = vk.get_api()

session = HTMLSession()


def get_user_city(user_id):
    user_info = vk_id.users.get(user_ids=user_id, fields='city')
    if user_info and 'city' in user_info[0]:
        return user_info[0]['city']['title']
    return None


def send_message(user_id, message, keyboard=None):
    vk_id.messages.send(
        user_id=user_id,
        message=message,
        random_id=0,
        keyboard=keyboard
    )


def get_coord_from_openweathermap(user_city_choise):
    user_city_translit = translit(user_city_choise, language_code='ru', reversed=True)
    response = requests.get(
        f"http://api.openweathermap.org/geo/1.0/direct?q={user_city_translit}&limit=1&appid={api_key}")
    if response.status_code == 200:
        data = response.json()
        lat_long = []
        for city in data:
            lat = city["lat"]
            long = city["lon"]
            lat_long.append(lat)
            lat_long.append(long)
            return lat_long  # широта и долгота
    else:
        return None


def get_weather_from_openweathermap(coord_lan, coord_long, day=0):
    response = requests.get(
        f"https://api.openweathermap.org/data/2.5/forecast?lat={coord_lan}&lon={coord_long}&appid={api_key}&units=metric")
    if response.status_code == 200:
        parameter = json.loads(response.text)
        weather = {}
        weather['temp_min'] = str(round(parameter['list'][day]['main']['temp_min']))
        weather['temp_max'] = str(round(parameter['list'][day]['main']['temp_max']))
        weather['wet'] = str(parameter['list'][day]['main']['humidity'])
        weather['wind'] = str(parameter['list'][day]['wind']['speed'])

        return weather  # собираем данные о погоде
    else:
        return None


def get_traffic_from_probkionline(user_city_choise):
    user_city_translit = translit(user_city_choise, language_code='ru', reversed=True)
    chrome_options = ChromeOptions()
    chrome_options.add_argument('--headless')
    browser = webdriver.Chrome(options=chrome_options)
    url_traffic = f'http://probki-online.ru/probki-online.php?city={user_city_translit}'
    browser.get(url_traffic)
    browser.implicitly_wait(10)
    traffic_element = browser.find_element(By.XPATH,
                                           '/html/body/div[5]/ymaps/ymaps/ymaps/ymaps[4]/ymaps[1]/ymaps[2]/ymaps[1]/ymaps/ymaps/ymaps[1]/ymaps[1]/ymaps/ymaps[2]/ymaps/ymaps')
    traffic_score = traffic_element.text
    browser.quit()
    return traffic_score


def get_afisha_from_afisharu(user_city_choise, day='segodnya'):
    spisok_from_afisha = []
    user_city_translit = translit(user_city_choise, language_code='ru', reversed=True)
    chrome_options = ChromeOptions()
    chrome_options.add_argument('--headless')
    browser = webdriver.Chrome(options=chrome_options)
    url_traffic = f'https://www.afisha.ru/{user_city_translit}/events/na-{day}/'
    browser.get(url_traffic)
    browser.implicitly_wait(10)

    afisha_perfomances_extract = browser.find_elements(By.CSS_SELECTOR, '.f5gWK')  # ищем все ссылки
    urls_list_from_afisha = []
    for i in range(5):
        urls_list_from_afisha.append(afisha_perfomances_extract[i].get_attribute('href'))  # сохраняем ссылки в списке

    for i in range(5):
        browser.get(urls_list_from_afisha[i])  # передаем ссылки поочередно
        browser.implicitly_wait(30)

        afisha_perfomance_name_extract = browser.find_element(By.CSS_SELECTOR,
                                                              '.fAgpL')  # извлекаем информацию о мероприятиях
        afisha_perfomance_name = afisha_perfomance_name_extract.get_attribute('textContent')  # название мероприятия

        try:
            afisha_price_extract = browser.find_element(By.CSS_SELECTOR, '.XMnSy')
            afisha_price_perfomance = afisha_price_extract.get_attribute('textContent')  # стоимость билетов
        except NoSuchElementException:
            afisha_price_perfomance = 'Нет данных о стоимости билетов'

        spisok_from_afisha.append((afisha_perfomance_name, afisha_price_perfomance, urls_list_from_afisha[i]))
    browser.quit()
    return spisok_from_afisha


def get_currency_from_financerambler():
    chrome_options = ChromeOptions()
    chrome_options.add_argument('--headless')
    browser = webdriver.Chrome(options=chrome_options)
    url_traffic = f'https://finance.rambler.ru/currencies/'
    browser.get(url_traffic)
    browser.implicitly_wait(10)

    tuple_currency = {}
    tuple_currency[browser.find_element(By.XPATH,
                                        '/html/body/div[8]/div/div/div[2]/div[2]/div[1]/div[2]/div/div/div[2]/a[37]/div[1]').text] = browser.find_element(
        By.XPATH, '/html/body/div[8]/div/div/div[2]/div[2]/div[1]/div[2]/div/div/div[2]/a[37]/div[4]').text  # доллар

    tuple_currency[browser.find_element(By.XPATH,
                                        '/html/body/div[8]/div/div/div[2]/div[2]/div[1]/div[2]/div/div/div[2]/a[13]/div[1]').text] = browser.find_element(
        By.XPATH, '/html/body/div[8]/div/div/div[2]/div[2]/div[1]/div[2]/div/div/div[2]/a[13]/div[4]').text  # евро

    tuple_currency[browser.find_element(By.XPATH,
                                        '/html/body/div[8]/div/div/div[2]/div[2]/div[1]/div[2]/div/div/div[2]/a[9]/div[1]').text] = browser.find_element(
        By.XPATH,
        '/html/body/div[8]/div/div/div[2]/div[2]/div[1]/div[2]/div/div/div[2]/a[9]/div[4]').text  # швейцарский франк

    tuple_currency[browser.find_element(By.XPATH,
                                        '/html/body/div[8]/div/div/div[2]/div[2]/div[1]/div[2]/div/div/div[2]/a[14]/div[1]').text] = browser.find_element(
        By.XPATH,
        '/html/body/div[8]/div/div/div[2]/div[2]/div[1]/div[2]/div/div/div[2]/a[14]/div[4]').text  # фунт стерлингов

    tuple_currency[browser.find_element(By.XPATH,
                                        '/html/body/div[8]/div/div/div[2]/div[2]/div[1]/div[2]/div/div/div[2]/a[15]/div[1]').text] = browser.find_element(
        By.XPATH,
        '/html/body/div[8]/div/div/div[2]/div[2]/div[1]/div[2]/div/div/div[2]/a[15]/div[4]').text  # грузинский лари

    return tuple_currency


user_city = ['']
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me and event.text:
            msg = event.text.lower()
            id = event.user_id
            city = get_user_city(id)

            try:
                if msg == 'начать':
                    keyboard = new_keyboard()
                    if city:
                        send_message(id, f'Ваш город {city}?', keyboard=keyboard_yes_no)
                        continue
                    else:
                        send_message(id, 'Выберите город', keyboard=keyboard)
                        continue
                keyboard = new_keyboard()

                if msg == 'да':
                    send_message(id, f'Город {city} зарегистрирован', keyboard=keyboard_menu)
                    user_city[0] = city
                elif msg == 'нет' or msg == 'выбрать другой город':
                    keyboard = new_keyboard()
                    send_message(id, 'Выберите город', keyboard=None)
                elif msg == 'погода':
                    coord_city = get_coord_from_openweathermap(user_city[0])
                    send_message(id, 'Выберите день', keyboard=keyboard_today_tomorrow_weather)
                elif msg == 'погода сегодня':
                    send_message(id, "Ищу информацию для вас...")
                    coord_city = get_coord_from_openweathermap(user_city[0])
                    user_town_choise = get_weather_from_openweathermap(coord_city[0], coord_city[1])
                    message = ('Сегодня температура воздуха в городе: ' + user_town_choise[
                        'temp_min'] + '... ' + user_town_choise['temp_max'] + ' °C,\n' + 'влажность воздуха: ' +
                               user_town_choise['wet'] + ' %, \n' + 'скорость ветра: ' +
                               user_town_choise['wind'] + ' м/сек')
                    send_message(id, message, keyboard=keyboard_menu)
                elif msg == 'погода завтра':
                    send_message(id, "Ищу информацию для вас...")
                    coord_city = get_coord_from_openweathermap(user_city[0])
                    user_town_choise = get_weather_from_openweathermap(coord_city[0], coord_city[1], 8)
                    message = ('Завтра ожидается температура воздуха в городе: ' + user_town_choise[
                        'temp_min'] + '... ' + user_town_choise['temp_max'] + ' °C,\n' + 'влажность воздуха: ' +
                               user_town_choise['wet'] + ' %, \n' + 'скорость ветра: ' +
                               user_town_choise['wind'] + ' м/сек')
                    send_message(id, message, keyboard=keyboard_menu)
                elif msg == 'пробки':
                    send_message(id, "Ищу информацию для вас...")
                    traffic_score_city_choise = get_traffic_from_probkionline(user_city[0])
                    send_message(id, f'Средний балл пробок в городе: {traffic_score_city_choise}',
                                 keyboard=keyboard_menu)
                elif msg == 'афиша':
                    coord_city = get_coord_from_openweathermap(user_city[0])
                    send_message(id, 'Выберите день', keyboard=keyboard_today_tomorrow_afisha)
                elif msg == 'афиша на сегодня':
                    send_message(id, "Ищу информацию для вас. Подождите,это может занять несколько минут.")
                    afisha = get_afisha_from_afisharu(user_city[0])
                    send_message(id, ('\n'.join([f'{i[0]}, Билеты: {i[1]}, {i[2]}' for i in afisha])),
                                 keyboard=keyboard_menu)
                elif msg == 'афиша на завтра':
                    send_message(id, "Ищу информацию для вас. Подождите,это может занять несколько минут.")
                    afisha = get_afisha_from_afisharu(user_city[0], 'zavtra')
                    send_message(id, ('\n'.join([f'{i[0]}, Билеты: {i[1]}, {i[2]}' for i in afisha])),
                                 keyboard=keyboard_menu)
                elif msg == 'валюта':
                    send_message(id, "Ищу информацию для вас...")
                    currency = get_currency_from_financerambler()
                    message = 'Курсы валют к российскому рублю:\n' + '\n'.join(
                        [f'1{key}: {value}₽' for key, value in currency.items()])
                    send_message(id, message, keyboard=keyboard_menu)
                else:
                    user_city[0] = msg
                    send_message(id, f'Город зарегистрирован', keyboard=keyboard_menu)

            except TimeoutException or NoSuchElementException:
                send_message(id, "Данные о мероприятиях не найдены, повторите запрос.")
        pass