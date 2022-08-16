import asyncio

from telethon.tl.types import User
from opentele import tl

from modules import tools


async def group_parser(client: tl.TelegramClient) -> None:
    """
        Parse the audience from the groups to which the user is added.
        Ignores bots and deleted accounts.
    """

    users = set()

    async for dialog in client.iter_dialogs(100):
        if dialog.is_group:
            await asyncio.sleep(3)

            async for user in client.iter_participants(dialog.id, aggressive=False):
                if user.bot is False and user.deleted is False:
                    users.add(f'{user.username or ""}, {user.phone or ""}\n')

    tools.write_users(users)


async def comment_parser(client: tl.TelegramClient) -> None:
    """
        Parse the audience from the comments of the channels in which the user is added.
        Ignores bots and deleted accounts.
    """

    users = set()

    async for dialog in client.iter_dialogs(100):
        if dialog.is_channel and dialog.message.replies:
            await asyncio.sleep(3)

            async for message in client.iter_messages(dialog.id, reply_to=dialog.message.id):
                sender = message.sender

                if isinstance(sender, User) and sender.bot is False and sender.deleted is False:
                    users.add(f'{sender.username or ""}, {sender.phone or ""}\n')

    tools.write_users(users)
