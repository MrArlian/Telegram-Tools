import itertools
import asyncio
import typing
import glob
import os

from opentele.api import UseCurrentSession
from opentele import exception, td, tl
from telethon import errors

from modules import StartEvent, LogVar, tools

from .utils import inviter, mailing, check_number, spam
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

        clients.append((client, profile))

    if len(clients) == 0:
        raise ValueError('Обновите profile в session/user')

    return itertools.cycle(clients)


async def _authorization_parser() -> tl.TelegramClient:

    try:
        tdesk = td.TDesktop('session/parser/tdata')
    except (exception.TFileNotFound, exception.OpenTeleException) as err:
        raise ValueError('Обновите tdata в session/parser') from err

    client = await tdesk.ToTelethon(flag=UseCurrentSession)
    await client.connect()

    return client


def start_script(app, event: StartEvent) -> None:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    logger = event.logger
    paths = event.paths

    account = paths.get('account')
    media = paths.get('media', '')
    phone = paths.get('phone')
    text = paths.get('text')


    try:
        clients = loop.run_until_complete(_authorization_accounts(logger))
        client = loop.run_until_complete(_authorization_parser())
    except ValueError as err:
        return event.logger.update(err)

    if event.is_channel_parser:
        loop.run_until_complete(comment_parser(client))
    elif event.is_group_parser:
        loop.run_until_complete(group_parser(client))

    if event.is_check_phone:
        loop.run_until_complete(check_number(clients, phone, logger))
    if event.is_mailing:
        loop.run_until_complete(mailing(clients, account, text, media, logger))
    if event.is_inviting:
        loop.run_until_complete(inviter(clients, account, event.channel, logger))
    if event.is_spam:
        loop.run_until_complete(spam(clients, account, text, logger))

    event.logger.update('Процесс завершен!')
    tools.change_state(app, 'normal')
    loop.close()
