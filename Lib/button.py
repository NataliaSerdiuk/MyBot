from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import vk_api, json


def new_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Начать', color=VkKeyboardColor.PRIMARY)
    return keyboard.get_keyboard()


def get_button(text, color):
    return {
        "action": {
            "type": "text",
            "payload": "{\"button\": \"" + "1" + "\"}",
            "label": f"{text}"
        },
        "color": f"{color}"
    }


keyboard_menu = {
    "one_time": False,
    "buttons": [
        [get_button('Афиша', 'positive'), get_button('Валюта', 'positive')],
        [get_button('Погода', 'positive'), get_button('Пробки', 'positive')],
        [get_button('Выбрать другой город', 'positive')]
    ]
}
keyboard_menu = json.dumps(keyboard_menu, ensure_ascii=False).encode('utf-8')
keyboard_menu = str(keyboard_menu.decode('utf-8'))

keyboard_today_tomorrow_weather = {
    "one_time": True,
    "buttons": [
        [get_button('Погода сегодня', 'positive'), get_button('Погода завтра', 'positive')]
    ]
}
keyboard_today_tomorrow_weather = json.dumps(keyboard_today_tomorrow_weather, ensure_ascii=False).encode('utf-8')
keyboard_today_tomorrow_weather = str(keyboard_today_tomorrow_weather.decode('utf-8'))

keyboard_today_tomorrow_afisha = {
    "one_time": True,
    "buttons": [
        [get_button('Афиша на сегодня', 'positive'), get_button('Афиша на завтра', 'positive')]
    ]
}
keyboard_today_tomorrow_afisha = json.dumps(keyboard_today_tomorrow_afisha, ensure_ascii=False).encode('utf-8')
keyboard_today_tomorrow_afisha = str(keyboard_today_tomorrow_afisha.decode('utf-8'))

keyboard_yes_no = {
    "one_time": True,
    "buttons": [
        [get_button('Да', 'positive'), get_button('Нет', 'positive')]
    ]
}
keyboard_yes_no = json.dumps(keyboard_yes_no, ensure_ascii=False).encode('utf-8')
keyboard_yes_no = str(keyboard_yes_no.decode('utf-8'))
