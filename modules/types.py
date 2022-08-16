import typing

from dataclasses import dataclass
from .variable import LogVar


@dataclass
class StartEvent:
    paths: dict
    channel: str

    logger: LogVar

    in_check_phone: typing.Optional[bool] = None
    is_inviting: typing.Optional[bool] = None
    is_mailing: typing.Optional[bool] = None
    is_report: typing.Optional[bool] = None
    is_spam: typing.Optional[bool] = None

    parser: typing.Optional[str] = None
