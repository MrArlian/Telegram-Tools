import itertools
import asyncio
import typing
import glob
import os

from opentele.api import UseCurrentSession
from opentele import exception, td, tl
from telethon import errors

from modules import StartEvent, LogVar, tools

from .utils import inviter, mailing, check_number
from .parser import group_parser, comment_parser


async def _authorization_accounts(logger: LogVar) -> typing.Iterator[tl.TelegramClient]:
    clients = []

    for profile_path in glob.glob('session/user/profile_*[0-9?]'):
        profile = os.path.basename(profile_path)

        try:
            tdesk = td.TDesktop(profile_path)
        except (exception.TFileNotFound, exception.OpenTeleException):
            logger.update(f'Ошибка авторизации для {profile}')
            continue

        client = await tdesk.ToTelethon(flag=UseCurrentSession)
        await client.connect()

        try:
            await client.get_me()
        except errors.FloodWaitError:
            continue

        clients.append(client)

    if len(clients) == 0:
        raise ValueError

    return itertools.cycle(clients)


async def _authorization_parser() -> tl.TelegramClient:
    tdesk = td.TDesktop('session/parser/tdata')

    client = await tdesk.ToTelethon(flag=UseCurrentSession)
    await client.connect()

    return client


def start_script(app, event: StartEvent) -> None:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    paths = event.paths
    account = paths.get('account')
    media = paths.get('media', '')
    phone = paths.get('phone')
    text = paths.get('text')

    try:
        clients = loop.run_until_complete(_authorization_accounts(event.logger))
    except ValueError:
        return event.logger.update('Обновите tdata в session/user')

    try:
        client = loop.run_until_complete(_authorization_parser())
    except (exception.TFileNotFound, exception.OpenTeleException):
        return event.logger.update('Ошибка авторизации для парсера.')

    if event.parser == 'channel':
        loop.run_until_complete(comment_parser(client))
    elif event.parser == 'group':
        loop.run_until_complete(group_parser(client))

    if event.in_check_phone:
        loop.run_until_complete(check_number(clients, phone))
    if event.is_mailing:
        loop.run_until_complete(mailing(clients, account, media, text))
    if event.is_inviting:
        loop.run_until_complete(inviter(clients, account, event.channel))
    if event.is_report:
        pass
    if event.is_spam:
        pass

    event.logger.update('Процесс завершен!')
    tools.change_state(app, 'normal')
    loop.close()
