# Импорт нужных библиотек и виджетов
import sqlite3
import sys

from PyQt5 import uic
from PyQt5.QtCore import QTimer, QTime, QDate
from PyQt5.QtWidgets import QMainWindow, QApplication
import datetime as dt

# Создание постоянных переменных
CON = sqlite3.connect('database.sqlite')
CUR = CON.cursor()
DAY = 86400
HOUR = 3600


# Создание главной страницы
class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()

        uic.loadUi('main_window.ui', self)
        self.list_active_events = []
        self.list_past_events = []
        self.check_active_event = False
        self.next_item = None
        self.input_events()
        self.timer_to_close_event()

        # Часы
        self.our_clock.setText(QTime.currentTime().toString('hh:mm:ss'))
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.show_clock)
        self.timer.start(1000)

        # Обновление для проверки событий
        self.timer_2 = QTimer(self)
        self.timer_2.timeout.connect(self.input_events)
        time_now = dt.datetime(2022, 12, 18, 23, 59, 35)

        self.timer_3 = QTimer(self)
        self.timer_3.timeout.connect(self.timer_to_close_event)

        self.timer_2.start(int((dt.timedelta(hours=int(time_now.strftime('%H')) + 1) - dt.timedelta(
            hours=int(time_now.strftime('%H')), minutes=int(time_now.strftime('%M')),
            seconds=int(time_now.strftime('%S')))).total_seconds() * 1000))

        self.timer_3.start(int((dt.timedelta(hours=int(time_now.strftime('%H')) + 1) - dt.timedelta(
            hours=int(time_now.strftime('%H')), minutes=int(time_now.strftime('%M')),
            seconds=int(time_now.strftime('%S')))).total_seconds() * 1000))

        self.timer_btn.clicked.connect(self.page_timer)
        self.add_event_btn.clicked.connect(self.page_calendar)
        self.delete_event.clicked.connect(self.page_deleting)

    # Вывод событий в соответствующие виджеты
    def input_events(self):
        self.future_evs_text.setText('')
        self.active_evs_text.setText('')
        cur_date = QDate.currentDate()
        cur_hour = QTime(QTime.currentTime())
        self.res = CUR.execute('SELECT * FROM Events ORDER BY date')
        for item in self.res:
            print(item, end='\n')
            ev_date = QDate(*self.convert_to_date(item[2]))
            ev_start_hour = QTime(int(item[4]), 0, 0)
            if item[5]:
                ev_end_hour = QTime(int(item[5]), 0, 0)
            else:
                ev_end_hour = None
            if ev_date > cur_date:
                self.future_evs_text.append(self.row_to_text(item))
            elif ev_date == cur_date:
                if cur_hour < ev_start_hour:
                    self.future_evs_text.append(self.row_to_text(item))
                elif ev_start_hour == cur_hour:
                    self.active_evs_text.append(self.row_to_text(item))
                    self.list_active_events.append(item)
                elif ev_end_hour:
                    if ev_start_hour <= cur_hour <= ev_end_hour:
                        self.active_evs_text.append(self.row_to_text(item))
                        self.list_active_events.append(item)
                    elif ev_end_hour < cur_hour:
                        self.list_past_events.append(item)
                elif ev_start_hour < cur_hour:
                    self.list_past_events.append(item)
            else:
                self.list_past_events.append(item)

            if not self.next_item or ev_date < QDate(*self.convert_to_date(self.next_item[2])):
                if item not in self.list_active_events and item not in self.list_past_events:
                    self.next_item = item
            self.timer_to_close_event()

    # Таймер до ближайшего события
    def timer_to_close_event(self):
        try:
            seconds_before_next_event = int((dt.datetime(int(self.next_item[2][6:]), int(self.next_item[2][3:5]),
                                                         int(self.next_item[2][:2]), int(self.next_item[4]), 0, 0,
                                                         0) - dt.datetime.now()).total_seconds())
            self.our_timer.setText(
                'Дней: {} Часов: {}'.format(seconds_before_next_event // DAY, seconds_before_next_event % DAY // HOUR))
        except Exception:
            self.our_timer.setText('Нет событий')

    # Формирование вывода
    def row_to_text(self, item):
        s = ''
        s += f'Событе №{item[0]}: {item[1].capitalize()}\n'
        if item[5]:
            s += f'Будет происходить {item[2]} с {item[4]}:00 до {item[5]}:00\n'
        else:
            s += f'Произойдёт {item[2]} в {item[4]}:00\n'
        s += f'Нужно будет:\n{item[3].capitalize()}'
        s += '\n'
        return s

    # Перевод в дату
    def convert_to_date(self, date):
        date_month_year = date.split('.')
        res = int(date_month_year[2]), int(date_month_year[1]), int(date_month_year[0])
        return res

    # Часы
    def show_clock(self):
        self.our_clock.setText(QTime.currentTime().toString('hh:mm:ss'))

    # Открытие страницы с таймером
    def page_timer(self):
        self.page_timer = Timer(self)
        self.page_timer.show()

    # Открытие страницы с добавлением событий
    def page_calendar(self):
        self.page_calendar = Calendar(self)
        self.page_calendar.show()

    def page_deleting(self):
        self.page_deleting = Deleting(self)
        self.page_deleting.show()


# Создание страницы с таймером
class Timer(QMainWindow):
    def __init__(self, *args):
        super().__init__()
        self.initUI(args)

    def initUI(self, args):
        uic.loadUi('timer.ui', self)

        self.start_btn.clicked.connect(self.start_timer)
        self.clear_btn.clicked.connect(self.start_timer)

        # Установление интервала таймера
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.show_time)
        self.timer.setInterval(1000)  # 1 sec
        self.time = 0

    # Вывод времени
    def show_time(self):
        self.time -= 1
        if self.time < 0:
            self.timer.stop()
            self.start_btn.setText("Запустить таймер")
            self.time = 0
        self.our_timer.setText('0' * (len(str(self.time // 3600)) < 2) + str(self.time // 3600) + ':' + '0' * (
                len(str(self.time % 3600 // 60)) < 2) + str(self.time % 3600 // 60) + ':' + '0' * (
                                       len(str(self.time % 60)) < 2) + str(self.time % 60))

    # Запуск таймера
    def start_timer(self):
        if self.sender().text() == "Запустить таймер":
            if not self.time:
                self.time = int(self.timeEdit.time().toString('HH')) * 3600 + int(
                    self.timeEdit.time().toString('mm')) * 60 + int(self.timeEdit.time().toString('ss'))
            self.our_timer.setText('0' * (len(str(self.time // 3600)) < 2) + str(self.time // 3600) + ':' + '0' * (
                    len(str(self.time % 3600 // 60)) < 2) + str(self.time % 3600 // 60) + ':' + '0' * (
                                           len(str(self.time % 60)) < 2) + str(self.time % 60))
            self.timer.start()
            self.start_btn.setText("Остановить")
        elif self.sender().text() == 'Остановить':
            self.timer.stop()
            self.start_btn.setText("Запустить таймер")

        else:
            self.timer.stop()
            self.start_btn.setText("Запустить таймер")
            self.our_timer.setText('00:00:00')
            self.time = 0
            self.timeEdit.setTime(QTime(0, 0, 0))


# Создание страницы с добавлением событий
class Calendar(QMainWindow):
    def __init__(self, *args):
        super().__init__()
        self.initUI(args)
        self.clear_input_btn.clicked.connect(self.clear_input)

    def initUI(self, args):
        uic.loadUi('calendar.ui', self)

        self.add_event_btn.clicked.connect(self.add_event)

    # Добавить событие
    def add_event(self):
        CUR.execute("""INSERT INTO events(title, date, start_hour, end_hour, description) VALUES(?, ?, ?, ?, ?)""",
                    (self.input_event_title.text(), self.calendar.selectedDate().toString('dd.MM.yyyy'),
                     self.input_event_start_time.time().toString('hh'),
                     self.input_event_end_time.time().toString('hh'), self.input_describe_event.text()))
        CON.commit()

        form.input_events()

    # Очистка ввода
    def clear_input(self):
        self.calendar.setSelectedDate(QDate.currentDate())
        time = QTime(0, 0)
        self.input_event_title.setText('')
        self.input_event_start_time.setTime(time)
        self.input_event_end_time.setTime(time)


# Создание страницы удаления событий
class Deleting(QMainWindow):
    def __init__(self, *args):
        super().__init__()
        self.initUI(args)

    def initUI(self, args):
        uic.loadUi('deleting.ui', self)

        self.delete_event.clicked.connect(self.delete_item)
        self.delete_all_events.clicked.connect(self.delete_all)

    # Удаление одного события
    def delete_item(self):
        index = self.input_item_index.text()
        CUR.execute("""DELETE from Events WHERE id = ?""", (int(index),))
        CON.commit()
        if form.next_item in form.list_active_events:
            del form.list_active_events[form.list_active_events.index(form.next_item)]
        form.next_item = None
        form.input_events()
        form.timer_to_close_event()

    # Удаление всех событий
    def delete_all(self):
        CUR.execute("""DELETE from Events""")
        CON.commit()
        form.list_active_events = []
        form.next_item = None
        form.input_events()
        form.timer_to_close_event()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = MyApp()
    form.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
