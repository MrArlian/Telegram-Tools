import typing

from dataclasses import dataclass
from .variable import LogVar


@dataclass
class StartEvent:
    paths: dict
    channel: str

    logger: LogVar

    is_channel_parser: typing.Optional[bool] = None
    is_group_parser: typing.Optional[bool] = None

    is_check_phone: typing.Optional[bool] = None
    is_inviting: typing.Optional[bool] = None
    is_mailing: typing.Optional[bool] = None
    is_report: typing.Optional[bool] = None
    is_spam: typing.Optional[bool] = None
