import asyncio
import typing
import os

from telethon.tl.functions.channels import InviteToChannelRequest
from telethon import errors
from opentele import tl

from modules import tools


async def inviter(clients: typing.Iterator[tl.TelegramClient],
                  path: str,
                  channel: str) -> None:
    """
        Invites users to a channel using multiple accounts.
    """

    for entity in tools.read_entitys(path):
        client = next(clients)

        try:
            await client(InviteToChannelRequest(channel, [entity]))
        except errors.FloodWaitError:
            continue
        except ValueError:
            continue

        await asyncio.sleep(1)


async def mailing(clients: typing.Iterator[tl.TelegramClient],
                  user_data_path: str,
                  media_path: str,
                  message_path: str) -> None:
    """
        Sends messages to users using multiple accounts.
    """

    with open(message_path, 'r', encoding='UTF-8') as file:
        message = file.read() or '.'

    for entity in tools.read_entitys(user_data_path):
        client = next(clients)

        try:
            if os.path.exists(media_path):
                await client.send_message(entity, message, file=media_path)
            else:
                await client.send_message(entity, message)
        except errors.FloodWaitError:
            continue
        except ValueError:
            continue

        await asyncio.sleep(1)


async def check_number(clients: typing.Iterator[tl.TelegramClient], path: str) -> None:
    """
        Checks the phone number for presence in the telegram database.
    """

    valid_phone = set()

    for phone in tools.read_entitys(path, True):
        client = next(clients)

        try:
            user = await client.get_entity(phone)
        except errors.FloodWaitError:
            continue
        except ValueError:
            continue

        valid_phone.add(f'{phone}, {user.username}\n')
        await asyncio.sleep(1)

    tools.write_phone(valid_phone)
