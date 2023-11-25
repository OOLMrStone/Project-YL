import io
import sys
import sqlite3
import time
import csv
import random

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog

with open("register.ui") as f:
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

    def add_new(self):
        self.login = self.login_line.text()
        self.password = self.password_line.text()
        if not self.cur.execute("SELECT login FROM Accounts WHERE (login=?)", (self.login,)).fetchall():
            if len(self.password) >= 8:
                self.cur.execute(f"INSERT INTO Accounts (login, password) VALUES (?, ?)",
                                 (self.login, self.password))
                self.status_lbl.setText("Registration completed successfully!")
                time.sleep(1)
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
                time.sleep(1)
                self.start(self.login)
            else:
                self.status_lbl.setText("Password or login is incorrect. Try again.")

    def start(self, login):
        self.mn = Main(login)
        self.mn.show()


class Main(QMainWindow):
    def __init__(self, login):
        super().__init__()
        f = io.StringIO(main_template)
        uic.loadUi(f, self)
        self.login = login
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
        lunch_1 = choose('SOUP%', (-70, 70))
        lunch_2 = choose('%STEAK%', (-40, 150))
        dinner = choose('RICE%', (-40, 100))
        extra_1 = choose('%CHICKEN%', (-50, 50))
        extra_2 = choose('%BEANS%', (-50, 50))
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
        pass

    def choose_file(self):
        fname = QFileDialog.getOpenFileName(self, 'Choose file:', '')[0]
        if fname:
            with open(fname, 'w') as f:
                f.write(self.menu.toPlainText())

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
        for line in self.day:
            self.menu.appendPlainText(f'{line[0]} - {line[1]} calories\n')

    def confirm(self):
        data = self.menu.toPlainText().split('\n\n')[-1].split()[1]
        self.fcur.execute(f"""CASE WHEN COL_LENGTH('accounts','{self.date_add}') IS NULL
                                  ALTER TABLE accounts ADD {self.date_add} integer;
                              """)
        self.fcur.execute(f"""INSERT INTO accounts ({self.date_add})
                                    WHERE (login='{self.login})
                                    VALUES (?)""", (data,))
        self.fcon.commit()



def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # ex = LoginWidget()
    # ex.show()
    mn = Main('osas')
    mn.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
