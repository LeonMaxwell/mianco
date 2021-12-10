import json
import uuid
import datetime
import os
import pytz

from mianto.settings import TIME_ZONE
from django.utils import timezone
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer

from profilemianto.models import ProfileMessages, ProfileMianto


@database_sync_to_async
def save_log_chats(user, id_room, logs):
    # Функция которая сохраняет логи. Записывает в базу данных Каналов названия файла после чего если такой файл есть
    # перезаписывает его. Работает в асинхронном режиме благодаря декоратору.
    profile = ProfileMianto.objects.get(login=user)
    messages = ProfileMessages.objects.get(first_interlocutor=profile, uuid_channel=id_room)
    file_name = f"{uuid.uuid4()}"
    with open(f"media/log/{file_name}.json", "w") as write_data:
        json.dump(logs, write_data)
        if messages.log_file:
            os.remove(f"media/log/{messages.log_file.name}.json")
    messages.log_file = file_name
    messages.save()


@database_sync_to_async
def loads_log_chats(user, id_room):
    # Функция для загрузки логов из файлов обоих собеседников для того что бы данные чата не потерялись.
    log_message_to = dict()
    log_message_from = dict()
    log_dict = dict()
    profile = ProfileMianto.objects.get(login=user)
    messages_to = ProfileMessages.objects.get(first_interlocutor=profile, uuid_channel=id_room).log_file.name
    if messages_to:
        with open(f"media/log/{messages_to}.json", 'r') as read_file:
            log_message_to = json.load(read_file)
    messages_from = ProfileMessages.objects.get(second_interlocutor=profile, uuid_channel=id_room).log_file.name
    if messages_from:
        with open(f"media/log/{messages_from}.json", 'r') as r:
            log_message_from = json.load(r)
    log_dict = {**log_message_to, **log_message_from}
    return log_dict


class ProfileConsumer(AsyncWebsocketConsumer):
    """
            Специальный асинхронный класс потребителей. Для работы с Chennels. Обеспечивает работу чата.
     """


    async def connect(self):
        # Функция которая вызывается при подключении пользователя к комнате.
        self.id_messages = self.scope['url_route']['kwargs']['id_messages']
        self.messages_group_name = 'chat_%s' % self.id_messages
        self.user = self.scope['user'].login
        self.logs_dict = dict()
        self.log_id = 0

        await self.channel_layer.group_add(
            self.messages_group_name,
            self.channel_name,
        )

        # подгружает логи из файла и выводит только тому кто запрашивает логи.
        loads = await loads_log_chats(self.user, self.id_messages)
        if loads:
            for i in loads.values():
                channel_layer = get_channel_layer()
                await channel_layer.send(self.channel_name, {
                    "type": "chat_message",
                    'user': i['user'],
                    'message': i['message'],
                    'date_time': i['date_time'],
                    'date_days': i['date_days'],
                    'second_message': i['second_message'],
                })

        await self.accept()

    async def disconnect(self, close_code):
        # функция при отключении от чата(переход на другую страницу/закрытие браузера).
        await self.channel_layer.group_discard(
            self.messages_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        # функция когда происходит отправка текста
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user = self.user
        date_now = datetime.datetime.utcnow().replace(tzinfo=pytz.timezone(TIME_ZONE)) + datetime.timedelta(hours=3)
        time_message = f"{date_now.hour}:{date_now.minute}"
        days_message = f"{date_now.day}"
        second_message = f"{date_now.second}"

        await self.channel_layer.group_send(
            self.messages_group_name,
            {
                'type': 'chat_message',
                'user': user,
                'message': message,
                'date_time': time_message,
                'date_days': days_message,
                'second_message': second_message,
            }
        )

    async def chat_message(self, event):
        # функция вызывается когда текст уже был передан
        message = event['message']
        user = event['user']
        date_time = event['date_time']
        date_days = event['date_days']
        second_message = event['second_message']
        self.logs_dict.update({f"{event['date_days']}-{event['date_time']}-{event['second_message']}": event})
        await save_log_chats(self.user, self.id_messages, self.logs_dict)

        await self.send(text_data=json.dumps({
            'user': user,
            'message': message,
            'date_time': date_time,
            'date_days': date_days,
            'second_message': second_message,
        }))


