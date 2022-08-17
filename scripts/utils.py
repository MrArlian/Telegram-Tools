import asyncio
import typing
import os

from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.custom.message import Message
from telethon import errors
from opentele import tl

from modules import LogVar, tools


async def inviter(clients: typing.Iterator[tl.TelegramClient],
                  path: str,
                  channel: str,
                  logger: LogVar) -> None:
    """
        Invites users to a channel using multiple accounts.
    """

    logger.update('Инвайтер запущен.')

    for entity in tools.read_entitys(path):
        client, profile = next(clients)

        try:
            await client(InviteToChannelRequest(channel, [entity]))
        except errors.FloodWaitError:
            continue
        except ValueError:
            continue

        logger.update(f'{profile} - Пригласил - {entity}')
        await asyncio.sleep(1)


async def mailing(clients: typing.Iterator[tl.TelegramClient],
                  user_path: str,
                  message_path: str,
                  media_path: str,
                  logger: LogVar) -> None:
    """
        Sends messages to users using multiple accounts.
    """


    if not os.path.exists(message_path):
        return

    logger.update('Рассылка запущена.')

    with open(message_path, 'r', encoding='UTF-8') as file:
        message = file.read() or '.'

    for entity in tools.read_entitys(user_path):
        client, profile = next(clients)

        try:
            if os.path.exists(media_path):
                await client.send_message(entity, message, file=media_path)
            else:
                await client.send_message(entity, message)
        except errors.FloodWaitError:
            continue
        except ValueError:
            continue

        logger.update(f'{profile} - Отправил сообщение - {entity}')
        await asyncio.sleep(1)


async def check_number(clients: typing.Iterator[tl.TelegramClient],
                       path: str,
                       logger: LogVar) -> None:
    """
        Checks the phone number for presence in the telegram database.
    """

    valid_phone = set()

    logger.update('Проверка номеров запущена.')

    for phone in tools.read_entitys(path, only_phone=True):
        client, _ = next(clients)

        try:
            user = await client.get_entity(phone)
        except errors.FloodWaitError:
            continue
        except ValueError:
            continue

        valid_phone.add(f'{phone}, {user.username}\n')
        await asyncio.sleep(1)

    tools.write_phone(valid_phone)


async def spam(clients: typing.Iterator[tl.TelegramClient],
               channel_path: str,
               message_path: str,
               logger: LogVar) -> None:
    """
        Spammer in channel comments. Uses the latest post to send the message.
    """

    if not os.path.exists(message_path):
        return

    logger.update('Спамер запущен.')

    with open(message_path, 'r', encoding='UTF-8') as file:
        text = file.read() or '.'

    for channel in tools.read_entitys(channel_path, only_username=True):
        client, _ = next(clients)

        try:
            message = await client.get_messages(channel, 1)[0]

            if isinstance(message, Message) and message.replies:
                await client.send_message(channel, text, comment_to=message.id)
        except errors.FloodWaitError:
            continue
        except ValueError:
            continue

        await asyncio.sleep(1)
