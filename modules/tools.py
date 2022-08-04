import datetime
import typing
import csv
import re


def write_users(users: typing.Iterable[tuple[int, str, str]]) -> None:
    today = datetime.datetime.now().date()

    with open(f'data/{today}.csv', 'w', encoding='UTF-8', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(('id', 'username', 'phone'))

        for user in users:
            writer.writerow(user)


def read_phone() -> typing.Iterable[str]:
    phones = []

    with open('data/phone.txt', 'r', encoding='UTF-8') as file:
        for phone in file.readlines():
            phone = phone.rsplit()[0]

            if re.match(r'^((\+(7|38|1))?\d{10})$', phone):
                phones.append(phone)

    return phones


def write_phone(phones: typing.Iterable[str]) -> None:
    with open('data/valid_phone.txt', 'a', encoding='UTF-8') as file:
        file.writelines(phones)
