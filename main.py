import io
import sys
import sqlite3
import csv
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
        f = io.StringIO(login_template)
        uic.loadUi(f, self)

        self.con = sqlite3.connect("accounts.db")
        self.cur = self.con.cursor()
        self.login = self.login_line.text()
        self.password = self.password_line.text()
        self.reg_btn.clicked.connect(self.add_new)
        self.login_btn.clicked.connect(self.log_in)
        self.pixmap = QPixmap('giga.jpg')
        self.image = QLabel(self)
        self.image.resize(645, 599)
        self.image.setPixmap(self.pixmap)
        self.image.lower()
        self.label.setStyleSheet("QLabel { color: white; }")
        self.status_lbl.setStyleSheet("QLabel { color: white; }")

    def add_new(self):
        self.login = self.login_line.text()
        self.password = self.password_line.text()
        if not self.cur.execute("SELECT login FROM Accounts WHERE (login=?)", (self.login,)).fetchall():
            if len(self.password) >= 8:
                self.cur.execute(f"INSERT INTO Accounts (login, password) VALUES (?, ?)",
                                 (self.login, self.password))
                self.status_lbl.setText("Registration completed successfully!")
                self.start(self.login)
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
                self.start(self.login)
            else:
                self.status_lbl.setText("Password or login is incorrect. Try again.")

    def start(self, login):
        self.mn = Main(login)
        self.mn.show()
        ex.close()


class Main(QMainWindow):
    def __init__(self, login):
        super().__init__()
        f = io.StringIO(main_template)
        uic.loadUi(f, self)

        self.goal = None
        self.login = login
        self.willkommen_lbl.setText(f"Welcome,\n{login}!")
        self.may_change = False
        self.day = []
        self.fcon = sqlite3.connect("accounts.db")
        self.fcur = self.fcon.cursor()
        self.get_menu_data()
        self.menu_btn.clicked.connect(self.get_menu)
        self.watch_btn.clicked.connect(self.draw_graph)
        self.save_btn.clicked.connect(self.choose_file)
        self.add_btn.clicked.connect(self.add_food)
        self.search_btn.clicked.connect(self.find)
        self.tkl_btn.clicked.connect(self.showday)
        self.confirm_btn.clicked.connect(self.confirm)
        self.goal_btn.clicked.connect(self.change_goal)
        self.table_btn.clicked.connect(self.view_database)

    def get_menu_data(self):
        with open("ABBREV.csv") as f:
            data = list(csv.reader(f, delimiter=';'))
            try:
                self.fcur.execute(f"""CREATE TABLE food (
                            NDB_No integer,
                            Shrt_Desc real,
                            Water real,
                            Energ_Kcal integer,
                            Protein real,
                            Lipid_Tot real,
                            Ash real,
                            Carbohydrt real,
                            Fiber_TD integer,
                            Sugar_Tot real
                            )""")
                for line in data[1:]:
                    if line:
                        self.fcur.execute(f"INSERT INTO food VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                          line[:10])
                self.fcon.commit()
            except sqlite3.OperationalError:
                return

    def get_menu(self):
        def choose(alike='%', between=(None, None)):
            """
            :param alike: name filter
            :param between: (left border move, right border move)
            :return: chosen food
            """

            if between[0] is None:
                btw_str = ''
            else:
                btw_str = f" AND Energ_Kcal BETWEEN {kcal_count / 6 + between[0]} AND {kcal_count / 4 + between[1]}"
            try:
                result = random.choice(self.fcur.execute(
                    f"""SELECT Shrt_Desc, Energ_Kcal FROM food WHERE Shrt_Desc LIKE '{alike}'""" + btw_str).fetchall())
            except IndexError:
                result = None
            return result

        kcal_count = int(self.cal_getter.value())
        if kcal_count < 200:
            self.menu.clear()
            self.menu.appendPlainText("It will be hard for you to survive...")
            return
        menu = []
        yogurt = choose('YOGURT%')
        breakfast = choose('EGG%', (-70, 70))
        if self.hp.isChecked():
            lunch_1 = choose('%PROTEIN%', (-150, 70))
            lunch_2 = choose('%PROTEIN%', (-70, 150))
            if self.veg.isChecked():
                extra_1 = choose('%SALAD DRSNG.POPPYSEED.CREAMY%')
            else:
                extra_1 = choose('%CHICKEN%', (-50, 50))
            extra_2 = choose('%BEANS%', (-50, 50))
        else:
            if self.veg.isChecked():
                lunch_1 = choose('%VEGETARIAN%', (-70, 70))
                lunch_2 = choose('%VEGETARIAN%', (-70, 70))
                extra_1 = choose('%YOGURT%', (-50, 50))
                extra_2 = choose('NOODLES.EGG%', (-50, 50))
            else:
                lunch_1 = choose('SOUP%', (-70, 70))
                lunch_2 = choose('%STEAK%', (-40, 150))
                extra_1 = choose('%CHICKEN%', (-50, 50))
                extra_2 = choose('%BEANS%', (-50, 50))
        dinner = choose('RICE%', (-40, 100))
        menu.extend([yogurt, breakfast, lunch_1, lunch_2, dinner, extra_1, extra_2])
        for food in range(len(menu)):
            kcal_count -= menu[food][1]
            if kcal_count < 0:
                index = food + 1
                break
        else:
            index = len(menu)
        self.menu.clear()
        for food in menu[:index]:
            if food is not None:
                self.menu.appendPlainText(f"{food[0]} - {food[1]} calories\n")
        self.menu.appendPlainText(f"Total: {int(self.cal_getter.value()) - kcal_count} calories.")

    def draw_graph(self):
        self.update()
        left, right = 0, 0
        from_date = str(self.from_d.date().toPyDate()).split('-')
        end_date = str(self.to_d.date().toPyDate()).split('-')
        user_data = list(self.fcur.execute(f"""SELECT * FROM accounts WHERE login='{self.login}'""").fetchone()[3:])
        user_days = [self.decrypt(column[1])
                     for column in self.fcur.execute("PRAGMA table_info('accounts')").fetchall()[3:]]
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

    def choose_file(self):
        fname = QFileDialog.getOpenFileName(self, 'Choose file:', '')[0]
        if fname:
            with open(fname, 'w') as nf:
                nf.write(self.menu.toPlainText())

    def add_food(self):
        chosen_food = self.fcur.execute(
            f"""SELECT Shrt_Desc, Energ_Kcal FROM food 
            WHERE Shrt_Desc LIKE '{self.comboBox.currentText().replace("'", "_")}'""").fetchone()
        self.day.append(chosen_food)

    def find(self):
        alike = self.search.text().upper()
        found = self.fcur.execute(f"""SELECT Shrt_Desc FROM food WHERE Shrt_Desc LIKE '%{alike}%'""").fetchall()
        self.comboBox.clear()
        self.comboBox.addItems([item[0] for item in found])

    def showday(self):
        self.menu.clear()
        if self.day:
            self.may_change = True
            for line in self.day:
                self.menu.appendPlainText(f'{line[0]} - {line[1]} calories\n')
        else:
            my_date = self.cpypt(str(self.date_add.date().toPyDate()).replace('-', '_'))
            kcal = self.fcur.execute(f"SELECT {my_date} FROM accounts WHERE login='{self.login}'").fetchone()[0]
            self.menu.setPlainText(f"You gain {kcal} calories that day.")

    def cpypt(self, date):
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

    def confirm(self):
        my_date = self.cpypt(str(self.date_add.date().toPyDate()).replace('-', '_'))
        if self.may_change:
            data = sum(int(product.split()[::-1][1]) for product in self.menu.toPlainText().split('\n\n'))
        else:
            data = sum([product[1] for product in self.day])
        print(data, self.login)

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
        self.fcur.execute(f"""SELECT * FROM food WHERE Shrt_Desc LIKE '%{self.table_query.text().upper()}%'""")
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
