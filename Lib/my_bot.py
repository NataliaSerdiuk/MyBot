import vk_api
from token_to import vk_token
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

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


def new_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Начать', color=VkKeyboardColor.PRIMARY)
    return keyboard.get_keyboard()


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me and event.text:
            msg = event.text.lower()
            id = event.user_id
            city = get_user_city(id)

            if msg == 'начать':
                if city:
                    send_message(id, f'Ваш город {city}?', keyboard=None)
                    break
                else:
                    keyboard = new_keyboard()
                    send_message(id, 'Выберите город', keyboard=keyboard)
                    break

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me and event.text:
            msg = event.text.lower()
            id = event.user_id
            city = get_user_city(id)

            if msg == 'да':
                user_city = city
                send_message(id, f'Город {user_city} зарегистрирован', keyboard=new_keyboard())
                break
            elif msg == 'нет':
                keyboard = new_keyboard()
                send_message(id, 'Выберите город', keyboard=keyboard)
            else:
                user_city = msg
                send_message(id, f'Город {user_city} зарегистрирован', keyboard=new_keyboard())
                break
