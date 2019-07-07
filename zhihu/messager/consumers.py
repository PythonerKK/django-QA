import json

from channels.consumer import AsyncConsumer
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from channels.layers import get_channel_layer


class MessagesConsumer(AsyncWebsocketConsumer):
    '''私信'''

    async def connect(self):
        if self.scope['user'].is_anonymous:
            await self.close()
        else:
            #加入聊天组
            await self.channel_layer.group_add(self.scope['user'].username,
                                         self.channel_name)
            await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        await self.send(text_data=json.dumps(text_data))

    async def disconnect(self, code):
        '''离开'''
        await self.channel_layer.group_discard(self.scope['user'].username,
                                         self.channel_name)
