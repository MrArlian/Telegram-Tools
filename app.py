import threading
import tkinter
import os

from tkinter import filedialog

from modules import LogVar, StartEvent, tools, styles
from scripts import start_script


root = tkinter.Tk()
root.title('Soft 1.0')
root.geometry('1080x540')
root.minsize(1080, 540)


FILE_PATHS = {}

CHANNEL = tkinter.StringVar(root, value='Введите канал')
IS_CHANNELS_PARSER = tkinter.BooleanVar(root)
IS_GROUPS_PARSER = tkinter.BooleanVar(root)
IN_CHECK_PHONE = tkinter.BooleanVar(root)
IS_INVITING = tkinter.BooleanVar(root)
IS_MAILING = tkinter.BooleanVar(root)
IS_REPORT = tkinter.BooleanVar(root)
IS_SPAM = tkinter.BooleanVar(root)

MEDIA_FILE_TYPE = (
    ('Photo File', ('*.jpg', '*.png')),
    ('Video File', '*.mp4'),
    ('Gif File', '*.gif')
)

TEXT_FILE_TYPE = (
    ('Text File', '*.txt'),
)

logger = LogVar(root)


def _load_file(name: str) -> None:

    if name == 'media':
        path = filedialog.askopenfilename(filetypes=MEDIA_FILE_TYPE)
    else:
        path = filedialog.askopenfilename(filetypes=TEXT_FILE_TYPE)

    if path:
        FILE_PATHS.update({name: path})
        logger.update(f'Файл для {name} добавлен.')


class MainApp(tkinter.Frame):

    def __init__(self, master: tkinter.Tk) -> None:
        super().__init__(master)

        self._create_toplevel()
        self._create_log_label()


    def _create_toplevel(self) -> None:
        toplevel = tkinter.Frame(root, styles.TOPLEVEL)
        toplevel.pack(side=tkinter.TOP, fill=tkinter.X)

        level_1 = tkinter.Frame(root, styles.LEVEL_1)
        level_1.pack(side=tkinter.TOP, fill=tkinter.X)


        self.button_1 = tkinter.Button(toplevel, styles.INNER_BUTTON_MANAGE, text='Аккаунты',
                                       command=lambda: _load_file('account'))
        self.button_1.pack(padx=14, side=tkinter.LEFT)

        self.button_2 = tkinter.Button(toplevel, styles.INNER_BUTTON_MANAGE, text='Номера',
                                       command=lambda: _load_file('phone'))
        self.button_2.pack(padx=14, side=tkinter.LEFT)

        self.button_3 = tkinter.Button(toplevel, styles.INNER_BUTTON_MANAGE, text='Медиа',
                                       command=lambda: _load_file('media'))
        self.button_3.pack(padx=14, side=tkinter.LEFT)

        self.button_4 = tkinter.Button(level_1, styles.INNER_BUTTON_MANAGE, text='Текст',
                                       command=lambda: _load_file('text'))
        self.button_4.pack(padx=14, side=tkinter.LEFT)


        self.entry = tkinter.Entry(toplevel, styles.INNER_ENTRY, textvariable=CHANNEL)
        self.entry.bind('<FocusIn>', lambda event: tools.focus_in(event, 'Введите канал'))
        self.entry.bind('<FocusOut>', lambda event: tools.focus_out(event, 'Введите канал'))
        self.entry.pack(padx=20, side=tkinter.LEFT)


        self.checkbox_1 = tkinter.Checkbutton(toplevel, styles.INNER_CHECKBOX, text='Репортер',
                                              variable=IS_REPORT)
        self.checkbox_1.pack(padx=15, side=tkinter.RIGHT)

        self.checkbox_2 = tkinter.Checkbutton(toplevel, styles.INNER_CHECKBOX, text='Инвайтер',
                                              variable=IS_INVITING)
        self.checkbox_2.pack(padx=15, side=tkinter.RIGHT)

        self.checkbox_3 = tkinter.Checkbutton(toplevel, styles.INNER_CHECKBOX, text='Спамер',
                                              variable=IS_SPAM)
        self.checkbox_3.pack(padx=15, side=tkinter.RIGHT)

        self.checkbox_4 = tkinter.Checkbutton(toplevel, styles.INNER_CHECKBOX, text='Рассыльщик',
                                              variable=IS_MAILING)
        self.checkbox_4.pack(padx=15, side=tkinter.RIGHT)

        self.checkbox_5 = tkinter.Checkbutton(level_1, styles.INNER_CHECKBOX, text='Парсинг групп',
                                              variable=IS_GROUPS_PARSER)
        self.checkbox_5.pack(padx=14, side=tkinter.RIGHT)

        self.checkbox_6 = tkinter.Checkbutton(level_1, styles.INNER_CHECKBOX, text='Парсинг каналов',
                                              variable=IS_CHANNELS_PARSER)
        self.checkbox_6.pack(padx=14, side=tkinter.RIGHT)

        self.checkbox_7 = tkinter.Checkbutton(level_1, styles.INNER_CHECKBOX, text='Проверка номеров',
                                              variable=IN_CHECK_PHONE)
        self.checkbox_7.pack(padx=14, side=tkinter.RIGHT)

        self.button_start = tkinter.Button(level_1, styles.INNER_BUTTON_START, text='Запустить',
                                           command=self.start_event)
        self.button_start.pack(padx=15, side=tkinter.LEFT)


    def _create_log_label(self) -> None:
        field = tkinter.Frame(root, styles.LOG_FIELD)
        field.pack(side=tkinter.TOP, fill=tkinter.BOTH)

        inner_field = tkinter.Frame(field, styles.INNER_LOG_FIELD)
        inner_field.pack(side=tkinter.TOP, fill=tkinter.BOTH)

        label = tkinter.Listbox(inner_field, styles.LOG_LABEL, listvariable=logger)
        label.pack(side=tkinter.TOP, fill=tkinter.BOTH)


    def start_event(self) -> None:

        if not any((IS_MAILING.get(), IS_SPAM.get(), IS_INVITING.get(), IS_REPORT.get(),
                    IN_CHECK_PHONE.get(), IS_CHANNELS_PARSER.get(), IS_GROUPS_PARSER.get())):
            return logger.update('Выберите хотя бы одну опцию.')

        if IN_CHECK_PHONE.get() and not FILE_PATHS.get('phone'):
            return logger.update('Добавьте файл с номерами.')
        if IS_INVITING.get() and not FILE_PATHS.get('account'):
            return logger.update('Добавьте файл с аккаунтами.')
        if IS_INVITING.get() and CHANNEL.get().lower() == 'введите канал':
            return logger.update('Напишите канал.')
        if IS_MAILING.get() and not FILE_PATHS.get('account'):
            return logger.update('Добавьте файл с аккаунтами.')
        if IS_MAILING.get() and not FILE_PATHS.get('text'):
            return logger.update('Добавьте файл с сообщением.')
        if IS_SPAM.get() and not FILE_PATHS.get('account'):
            return logger.update('Добавьте файл с каналами.')
        if IS_REPORT.get() and not FILE_PATHS.get('account'):
            return logger.update('Добавьте файл с аккаунтами.')

        tools.change_state(self, tkinter.DISABLED)
        logger.update('Скрипт начал работу.')

        event = StartEvent(
            FILE_PATHS, CHANNEL.get(), logger, IS_CHANNELS_PARSER.get(), IS_GROUPS_PARSER.get(),
            IN_CHECK_PHONE.get(), IS_INVITING.get(), IS_MAILING.get(),
            IS_REPORT.get(), IS_SPAM.get()
        )
        threading.Thread(target=start_script, args=(self, event)).start()


def main() -> None:
    if not os.path.isdir('data'):
        os.mkdir('data')
    if not os.path.isdir('session'):
        os.makedirs('session/parser')
        os.makedirs('session/user')

    app = MainApp(root)
    app.mainloop()


if __name__ == '__main__':
    main()
