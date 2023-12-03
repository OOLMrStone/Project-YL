import io
import sys
import sqlite3
import random
import pyqtgraph as pg

from datetime import datetime
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableWidgetItem, QLabel

with open("register.ui", encoding="utf8") as f:
    login_template = f.read()
with open("mainWindow.ui") as f:
    main_template = f.read()


class LoginWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        base = io.StringIO(login_template)
        uic.loadUi(base, self)

        self.con = sqlite3.connect("accounts.db")
        self.cur = self.con.cursor()
        self.login = self.login_line.text()
        self.password = self.password_line.text()
        self.reg_btn.clicked.connect(self.register_user)
        self.login_btn.clicked.connect(self.log_in)
        self.pixmap = QPixmap('giga.jpg')
        self.image = QLabel(self)
        self.image.resize(645, 599)
        self.image.setPixmap(self.pixmap)
        self.image.lower()
        self.label.setStyleSheet("QLabel { color: white; }")
        self.status_lbl.setStyleSheet("QLabel { color: white; }")

    def register_user(self):
        self.login = self.login_line.text()
        self.password = self.password_line.text()
        if not self.cur.execute("SELECT login FROM Accounts WHERE (login=?)", (self.login,)).fetchall():
            if len(self.password) >= 8:
                self.cur.execute(f"INSERT INTO Accounts (login, password) VALUES (?, ?)",
                                 (self.login, self.password))
                self.status_lbl.setText("Registration completed successfully!")
                self.run_main_window(self.login)
            else:
                self.status_lbl.setText("Password has to contain at least 8 chars.")
        else:
            self.status_lbl.setText("This login already exists.")
        self.con.commit()

    def log_in(self):
        self.login = self.login_line.text()
        self.password = self.password_line.text()
        if not self.cur.execute("SELECT login FROM Accounts WHERE (login=?)",
                                (self.login,)).fetchall():
            self.status_lbl.setText(f'There is no login "{self.login}".')
        else:
            if self.cur.execute("SELECT password FROM Accounts WHERE (login=? AND password=?)",
                                (self.login, self.password)).fetchall():
                self.status_lbl.setText(f"Welcome, {self.login}!")
                self.run_main_window(self.login)
            else:
                self.status_lbl.setText("Password or login is incorrect. Try again.")

    def run_main_window(self, login):
        self.mn = Main(login)
        self.mn.show()
        ex.close()


class Main(QMainWindow):
    def __init__(self, login):
        super().__init__()
        main_base = io.StringIO(main_template)
        uic.loadUi(main_base, self)

        self.goal = None
        self.login = login
        self.willkommen_lbl.setText(f"Welcome,\n{login}!")
        self.day = []
        self.fcon = sqlite3.connect("accounts.db")
        self.fcur = self.fcon.cursor()
        self.menu_btn.clicked.connect(self.create_menu)
        self.watch_btn.clicked.connect(self.draw_graph)
        self.save_btn.clicked.connect(self.save_menu)
        self.add_btn.clicked.connect(self.add_food)
        self.search_btn.clicked.connect(self.find_food)
        self.clear_btn.clicked.connect(self.clear_day)
        self.confirm_btn.clicked.connect(self.confirm)
        self.goal_btn.clicked.connect(self.change_goal)
        self.table_btn.clicked.connect(self.view_database)

    def choose_food(self, day_kcal, alike='%', between=(0, 0)):
        """
        :param day_kcal: amount of kcal for day
        :param alike: name filter
        :param between: (deviation) to the left, to the right
        :return: chosen food
        """

        result = None
        repeat = 1
        while result is None:
            try:
                if between[0] == 0:
                    btw_str = ''
                else:
                    btw_str = f" AND Energ_Kcal BETWEEN {day_kcal / 6 + between[0]} AND {day_kcal / 4 + between[1]}"
                result = (random.choice(self.fcur.execute(
                    f"""SELECT Shrt_Desc, Energ_Kcal FROM food 
                    WHERE Shrt_Desc LIKE '{alike}'""" + btw_str).fetchall()), repeat)
            except IndexError:
                day_kcal //= 2
                repeat *= 2
        return result

    def create_menu(self):
        kcal_count = int(self.cal_getter.value())
        if kcal_count < 500:
            self.menu.clear()
            self.menu.appendPlainText("It will be hard for you to survive...")
            return
        menu = []
        yogurt = self.choose_food(kcal_count, 'YOGURT%')
        breakfast = self.choose_food(kcal_count, 'EGG%', (-70, 70))
        if self.hp.isChecked():
            lunch_1 = self.choose_food(kcal_count, '%PROTEIN%', (-150, 70))
            lunch_2 = self.choose_food(kcal_count, '%PROTEIN%', (-70, 150))
            if self.veg.isChecked():
                extra_1 = self.choose_food(kcal_count, '%SALAD DRSNG.POPPYSEED.CREAMY%')
            else:
                extra_1 = self.choose_food(kcal_count, '%CHICKEN%', (-50, 50))
            extra_2 = self.choose_food(kcal_count, '%BEANS%', (-50, 50))
        else:
            if self.veg.isChecked():
                lunch_1 = self.choose_food(kcal_count, '%VEGETARIAN%', (-70, 70))
                lunch_2 = self.choose_food(kcal_count, '%VEGETARIAN%', (-70, 70))
                extra_1 = self.choose_food(kcal_count, '%YOGURT%', (-50, 50))
                extra_2 = self.choose_food(kcal_count, 'NOODLES.EGG%', (-50, 50))
            else:
                lunch_1 = self.choose_food(kcal_count, 'SOUP%', (-70, 70))
                lunch_2 = self.choose_food(kcal_count, '%STEAK%', (-40, 150))
                extra_1 = self.choose_food(kcal_count, '%CHICKEN%', (-50, 50))
                extra_2 = self.choose_food(kcal_count, '%BEANS%', (-50, 50))
        dinner = self.choose_food(kcal_count, 'RICE%', (-40, 100))
        menu.extend([yogurt, breakfast, lunch_1, lunch_2, dinner, extra_1, extra_2])
        kcal_count_copy = kcal_count
        for food in range(len(menu)):
            kcal_count_copy -= menu[food][0][1] * menu[food][1]
            if abs(kcal_count_copy) < max(100.0, kcal_count * 0.1):
                index = food + 1
                break
        else:
            index = len(menu)
        self.menu.clear()
        for food in menu[:index]:
            if food[0] is not None:
                for _ in range(food[1]):
                    self.menu.appendPlainText(f"{food[0][0]} - {food[0][1]} calories\n")
        self.menu.appendPlainText(f"Total: {kcal_count - kcal_count_copy} calories.")

    def draw_graph(self):
        self.update()
        left, right = 0, 0
        from_date = str(self.from_d.date().toPyDate()).split('-')
        end_date = str(self.to_d.date().toPyDate()).split('-')
        user_data = list(self.fcur.execute(f"""SELECT * FROM accounts WHERE login='{self.login}'""").fetchone()[3:])
        user_days = [self.decrypt(column[1])
                     for column in self.fcur.execute("PRAGMA table_info('accounts')").fetchall()[3:]]
        for i in range(len(user_data)):
            if user_data[i] is None:
                user_days[i] = ''
        user_data = list(filter(lambda x: x, user_data))
        user_days = list(filter(lambda x: x, user_days))
        cp = user_data.copy()
        user_data.sort(key=lambda value: user_days[cp.index(value)].split('_'))
        user_days.sort(key=lambda day: day.split('_'))
        for i in range(len(user_days)):
            if user_days[i].split('_') >= from_date:
                left = i
                break
        for i in range(len(user_days) - 1, -1, -1):
            if user_days[i].split('_') <= end_date:
                right = i + 1
                break
        user_days = [datetime.strptime(day, "%Y_%m_%d") for day in user_days]
        user_data = user_data[left:right]
        user_days = user_days[left:right]
        plt = pg.plot(title='kcal_graph')
        plt.plot(x=[day.timestamp() for day in user_days], y=user_data, symbol='o')
        if self.goal:
            plt.addLine(y=self.goal, pen='y')

    def save_menu(self):
        fname = QFileDialog.getOpenFileName(self, 'Choose file:', '')[0]
        if fname:
            with open(fname, 'w') as nf:
                nf.write(self.menu.toPlainText())

    def add_food(self):  # adds user-selected food to "day" variable
        chosen_food = self.fcur.execute(
            f"""SELECT Shrt_Desc, Energ_Kcal FROM food 
            WHERE Shrt_Desc LIKE '{self.comboBox.currentText().replace("'", "_")}'""").fetchone()
        self.day.append(chosen_food)
        self.menu.clear()
        for line in self.day:
            self.menu.appendPlainText(f'{line[0]} - {line[1]} calories\n')

    def find_food(self):  # finds user-selected food to add it to the comboBox
        alike = self.search.text().upper()
        found = self.fcur.execute(f"""SELECT Shrt_Desc FROM food
                                      WHERE Shrt_Desc LIKE '%{alike.replace("'", '_')}%'""").fetchall()
        self.comboBox.clear()
        self.comboBox.addItems([item[0] for item in found])

    def clear_day(self):
        self.menu.clear()
        self.day.clear()

    # need these two functions below because database is unable to work with number-alike headers
    def encpypt(self, date):
        crypto = {'0': 'a',
                  '1': 'b',
                  '2': 'c',
                  '3': 'd',
                  '4': 'e',
                  '5': 'f',
                  '6': 'g',
                  '7': 'h',
                  '8': 'i',
                  '9': 'j',
                  '_': '_'}

        result = ''
        for char in date:
            result += crypto[char]
        return result

    def decrypt(self, cr_date):
        crypto = {'a': '0',
                  'b': '1',
                  'c': '2',
                  'd': '3',
                  'e': '4',
                  'f': '5',
                  'g': '6',
                  'h': '7',
                  'i': '8',
                  'j': '9',
                  '_': '_'}

        result = ''
        for char in cr_date:
            result += crypto[char]
        return result

    def confirm(self):  # saves "day" variable to a database
        my_date = self.encpypt(str(self.date_add.date().toPyDate()).replace('-', '_'))
        data = sum(int(product.split()[::-1][1]) for product in self.menu.toPlainText().split('\n\n'))

        self.fcur.execute("PRAGMA table_info('accounts')")
        columns = [column[1] for column in self.fcur.fetchall()]
        if f"{my_date}" not in columns:
            self.fcur.execute(f"ALTER TABLE accounts ADD COLUMN {my_date} INTEGER")

        self.fcur.execute(f"""UPDATE accounts SET {my_date}=? WHERE login=?""", (data, self.login))

        self.fcon.commit()
        self.day_lbl.setText(f"Day has been saved!\nTotal: {data} calories.")

    def change_goal(self):
        self.goal = self.goal_inf.text()

    def view_database(self):
        self.fcur.execute(f"""SELECT * FROM food 
                              WHERE Shrt_Desc LIKE '%{self.table_query.text().upper().replace("'", '_')}%'""")
        data = self.fcur.fetchall()
        self.table.setRowCount(len(data))
        self.table.setHorizontalHeaderLabels(["Name", "Water_(g)", "Kcal",
                                              "Protein_(g)", "Lipid_Tot_(g)", "Ash_(g)", "Carbohydrt_(g)",
                                              "Fiber_TD_(g)", "Sugar_Tot_(g)"])
        if not data:
            return
        self.table.setColumnCount(len(data[0]) - 1)
        for i, elem in enumerate(data):
            for j, val in enumerate(elem[1:]):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = LoginWidget()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
