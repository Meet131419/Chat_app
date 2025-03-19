import json
import pusher
from datetime import datetime
from django.utils.timezone import localtime
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import GroupMessage, Register, ChatGroup
from django.conf import settings

# Pusher instance
pusher_client = pusher.Pusher(
    app_id=settings.PUSHER_APP_ID,
    key=settings.PUSHER_KEY,
    secret=settings.PUSHER_SECRET,
    cluster=settings.PUSHER_CLUSTER,
    ssl=True
)

@database_sync_to_async
def save_message(message, author, group,  file=None, file_type=None):
    msg = GroupMessage.objects.create(
        body=message,
        author=author,
        group=group,
        file=file,
        file_type=file_type,
    )
    return msg

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = self.scope["url_route"]["kwargs"]["group_name"]
        self.room_group_name = f"chat_{self.group_name}"

        if self.channel_layer:
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if self.channel_layer:
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message")
        email = data.get("email")
        file_url = data.get("file_url")
        file_type = data.get("file_type")

        # Fetch the user and chat group
        logged_in_user = await self.get_user_by_email(email)
        chat_group = await self.get_group_by_name(self.group_name)

        # Save message
        msg = await save_message(
            message=message,
            author=logged_in_user,
            group=chat_group,
            file=file_url,
            file_type=file_type,
        )

        # Format the time before sending
        message_time = localtime(msg.created).strftime('%I:%M %p')
        author_name = msg.author.First_name

        # Broadcast the message to the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "email": email,
                "author_name": author_name,
                "message_time": message_time,  # Send formatted time
                "file_url": msg.file_url,
                "file_type": file_type,
            }
        )

    async def chat_message(self, event):
        # Send the message with time to the frontend
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "email": event["email"],
            "author_name": event["author_name"],
            "message_time": event["message_time"],  # Send formatted time
            "file_url": event.get("file_url"),
            "file_type": event.get("file_type"),
        }))

    @database_sync_to_async
    def get_user_by_email(self, email):
        return Register.objects.get(email=email)

    @database_sync_to_async
    def get_group_by_name(self, group_name):
        return ChatGroup.objects.get(group_name=group_name)
