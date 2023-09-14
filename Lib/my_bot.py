from token_to import *
from vk_api.longpoll import VkLongPoll, VkEventType
from transliterate import translit
from button import *
import requests


vk = vk_api.VkApi(token=vk_token)
longpoll = VkLongPoll(vk)
vk_id = vk.get_api()


def get_user_city(user_id):
    user_info = vk_id.users.get(user_ids=user_id, fields='city')
    if user_info:
        return user_info[0]['city']['title']
    return None


def send_message(user_id, message, keyboard=None):
    vk_id.messages.send(
        user_id=user_id,
        message=message,
        random_id=0,
        keyboard=keyboard
    )

def get_weather(user_city_choise):
    user_city_translit = translit(user_city_choise, language_code='ru', reversed=True)
    response = requests.get(f"https://api.openweathermap.org/geo/1.0/direct?q={user_city_translit}&limit=1&appid={api_key}")
    if response.status_code == 200:
        data = response.json()
        for city in data:
            lat = city["lat"]
            long = city["lon"]
            url_weath = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={long}&appid={api_key}"
            response = requests.get(url_weath)
            if response.status_code == 200:
                data = response.json()
                temp_kelv = data["list"][0]["main"]["temp"]
                temp_cels = round(temp_kelv - 273.15)
                return temp_cels
            else:
                return None
    else:
        return None



user_city = ['']
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me and event.text:
            msg = event.text.lower()
            id = event.user_id
            city = get_user_city(id)
            if msg == 'начать':
                if city:
                    send_message(id, f'Ваш город {city}?', keyboard=None)
                else:
                    keyboard = new_keyboard()
                    send_message(id, 'Выберите город', keyboard=keyboard)
            elif msg == 'да':
                send_message(id, f'Город {city} зарегистрирован', keyboard=keyboard_menu)
                user_city[0] = city
            elif msg == 'нет':
                keyboard = new_keyboard()
                send_message(id, 'Выберите город', keyboard=None)
            elif msg == 'погода':
                print('town:', city, user_city[0])
                town = get_weather(user_city[0])
                send_message(id,f'Температура воздуха в городе: {town} °C', keyboard=keyboard_menu)

            else:
                user_city[0] = msg
                send_message(id, f'Город {user_city[0]} зарегистрирован', keyboard=keyboard_menu)
            print(user_city)
