import asyncio
import ast
import os

from telethon.tl.functions.channels import InviteToChannelRequest
from telethon import TelegramClient, errors
from telethon.tl.types import User

from configobj import ConfigObj

from modules import tools


cfg = ConfigObj('config.cfg')

ACCOUNTS = ast.literal_eval(cfg.get('ACCOUNTS'))
PARSER_PASSWORD = cfg.get('PARSER_PASSWORD')
PARSER_PHONE = cfg.get('PARSER_PHONE')
API_HASH = cfg.get('API_HASH')
API_ID = cfg.get('API_ID')

CHECK_NUMBER = cfg.as_bool('CHECK_NUMBER')
PARSER_TYPE = cfg.get('PARSER_TYPE')
INVITING = cfg.as_bool('INVITING')
MAILING = cfg.as_bool('MAILING')

MESSAGE = cfg.get('MESSAGE')
CHANNEL = cfg.get('CHANNEL')

USER_DATA_PATH = cfg.get('USER_DATA_PATH')
PHONE_PATH = cfg.get('PHONE_PATH')
MEDIA_PATH = cfg.get('MEDIA_PATH')


if not os.path.isdir('data'):
    os.mkdir('data')
if not os.path.isdir('session'):
    os.makedirs('session/parser')
    os.makedirs('session/user')

parser = TelegramClient('session/parser/parser', API_ID, API_HASH)
parser.start(PARSER_PHONE, PARSER_PASSWORD)


async def _authorization() -> list[TelegramClient]:
    clients = []

    for name in ACCOUNTS:
        phone, password = ACCOUNTS[name]

        client = TelegramClient(f'session/user/{name}', API_ID, API_HASH)
        await client.start(phone, password)

        try:
            await client.get_me()
        except errors.FloodWaitError:
            continue

        clients.append(client)

    return clients


async def group_parser():
    """
        Parse the audience from the groups to which the user is added.
        Ignores bots.
    """

    users = set()

    async for dialog in parser.iter_dialogs(100):
        if dialog.is_group:
            await asyncio.sleep(3)

            async for user in parser.iter_participants(dialog.id, aggressive=False):
                if user.bot is False and user.deleted is False:
                    users.add(f'{user.username or ""}, {user.phone or ""}\n')

    tools.write_users(users)


async def comment_parser():
    """
        Parse the audience from the comments of the channels in which the user is added.
    """

    users = set()

    async for dialog in parser.iter_dialogs(100):
        if dialog.is_channel:
            await asyncio.sleep(3)

            try:
                async for message in parser.iter_messages(dialog.id, reply_to=dialog.message.id):
                    sender = message.sender

                    if isinstance(sender, User) and sender.bot is False and sender.deleted is False:
                        users.add(f'{sender.username or ""}, {sender.phone or ""}\n')
            except (errors.PeerIdInvalidError, errors.MsgIdInvalidError):
                continue

    tools.write_users(users)


async def inviter() -> None:
    """
        Invites users to a channel using multiple accounts.
    """

    clients = await _authorization()
    step = 0

    for entity in tools.read_entitys(USER_DATA_PATH):
        client = clients[step]

        try:
            await client(InviteToChannelRequest(CHANNEL, [entity]))
        except errors.FloodWaitError:
            continue
        except ValueError:
            continue

        if len(clients) - 1 >= step + 1:
            step += 1
        else:
            step = 0

        await asyncio.sleep(1)


async def mailing() -> None:
    """
        Sends messages to users using multiple accounts.
    """

    clients = await _authorization()
    step = 0

    for entity in tools.read_entitys(USER_DATA_PATH):
        client = clients[step]

        try:
            if os.path.exists(MEDIA_PATH):
                await client.send_message(entity, MESSAGE, file=MEDIA_PATH)
            else:
                await client.send_message(entity, MESSAGE)
        except errors.FloodWaitError:
            continue
        except ValueError:
            continue

        if len(clients) - 1 >= step + 1:
            step += 1
        else:
            step = 0

        await asyncio.sleep(1)


async def check_number() -> None:
    """
        Checks the phone number for presence in the telegram database.
    """

    clients = await _authorization()
    valid_phone = set()
    step = 0

    for phone in tools.read_entitys(PHONE_PATH, True):
        client = clients[step]

        try:
            user = await client.get_entity(phone)
        except errors.FloodWaitError:
            continue
        except ValueError:
            continue

        if len(clients) - 1 >= step + 1:
            step += 1
        else:
            step = 0

        valid_phone.add(f'{phone}, {user.username}\n')
        await asyncio.sleep(1)

    tools.write_phone(valid_phone)


async def main() -> None:
    print('Script started...')

    if PARSER_TYPE == 'group':
        await group_parser()
    elif PARSER_TYPE == 'comment':
        await comment_parser()

    if INVITING:
        await inviter()
    if MAILING:
        await mailing()
    if CHECK_NUMBER:
        await check_number()


if __name__ == '__main__':
    parser.loop.run_until_complete(main())
