import datetime
import tkinter
import typing
import re
import os


def write_users(users: typing.Iterable[str]) -> None:
    today = datetime.datetime.now().date()

    with open(f'data/{today}.txt', 'a', encoding='UTF-8') as file:
        file.writelines(users)


def write_phone(phones: typing.Iterable[str]) -> None:
    with open('data/valid_phone.txt', 'a', encoding='UTF-8') as file:
        file.writelines(phones)


def read_entitys(path: str, only_phone: bool = False) -> typing.Iterable[str]:
    entitys = []

    if not os.path.exists(path):
        return []

    with open(path, 'r', encoding='UTF-8') as file:
        for entity in file.readlines():
            entity = entity.rsplit()[0]

            if re.match(r'^([a-z0-9_]{5,32})$', entity.lower()) and only_phone is False:
                entitys.append(entity)
            elif re.match(r'^((\+(7|38|1))?\d{10})$', entity):
                entitys.append(entity)

    return entitys


def focus_in(event: tkinter.Event, string: str) -> None:
    if event.widget.get() == string:
        event.widget.delete(0, tkinter.END)


def focus_out(event: tkinter.Event, string: str) -> None:
    if event.widget.get() == '':
        event.widget.insert(0, string)


def change_state(_app, state: typing.Literal['normal', 'disabled']) -> None:
    _app.button_start.config(state=state)
    _app.button_1.config(state=state)
    _app.button_2.config(state=state)
    _app.button_3.config(state=state)
    _app.button_4.config(state=state)

    _app.entry.config(state=state)

    _app.checkbox_1.config(state=state)
    _app.checkbox_2.config(state=state)
    _app.checkbox_3.config(state=state)
    _app.checkbox_4.config(state=state)
    _app.checkbox_5.config(state=state)
    _app.checkbox_6.config(state=state)
    _app.checkbox_7.config(state=state)
