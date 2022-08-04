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


async def group_parser() -> set[tuple[int, str, str]]:
    """
        Parse the audience from the groups to which the user is added.
        Ignores bots.
    """

    users = set()

    async for dialog in parser.iter_dialogs(1):
        if dialog.is_group:
            await asyncio.sleep(3)

            async for user in parser.iter_participants(dialog.id, aggressive=False):
                if user.bot is False and user.deleted is False:
                    users.add((user.id, user.username or '', user.phone or ''))

    tools.write_users(users)
    return users


async def comment_parser() -> set[tuple[int, str, str]]:
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
                        users.add((sender.id, sender.username or '', sender.phone or ''))
            except (errors.PeerIdInvalidError, errors.MsgIdInvalidError):
                continue

    tools.write_users(users)
    return users


async def inviter(users: set[tuple[int, str, str]]) -> None:
    """
        Invites users to a channel using multiple accounts.
    """

    clients = await _authorization()
    step = 0

    for user_id, _, _ in users:
        client = clients[step]

        try:
            await client(InviteToChannelRequest(CHANNEL, [user_id]))
        except errors.FloodWaitError:
            continue
        except ValueError:
            continue

        if len(clients) - 1 >= step + 1:
            step += 1
        else:
            step = 0

        await asyncio.sleep(1)


async def mailing(users: set[tuple[int, str, str]]) -> None:
    """
        Sends messages to users using multiple accounts.
    """

    clients = await _authorization()
    step = 0

    for user_id, _, _ in users:
        client = clients[step]

        try:
            await client.send_message(user_id, MESSAGE)
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

    for phone in tools.read_phone():
        client = clients[step]

        try:
            await client.get_input_entity(phone)
        except errors.FloodWaitError:
            continue
        except ValueError:
            continue

        if len(clients) - 1 >= step + 1:
            step += 1
        else:
            step = 0

        valid_phone.add(f'{phone}\n')
        await asyncio.sleep(1)

    tools.write_phone(valid_phone)


async def main() -> None:
    users = []

    print('Script started...')


    if PARSER_TYPE == 'group':
        users = await group_parser()
    elif PARSER_TYPE == 'comment':
        users = await comment_parser()

    if INVITING:
        await inviter(users)
    if MAILING:
        await mailing(users)
    if CHECK_NUMBER:
        await check_number()


if __name__ == '__main__':
    parser.loop.run_until_complete(main())
