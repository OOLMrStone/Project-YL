import io
import sys
import sqlite3
import time

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow

login_template = """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>MainWindow</class>
 <widget class="QMainWindow" name="MainWindow">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>645</width>
    <height>599</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>вход</string>
  </property>
  <property name="toolButtonStyle">
   <enum>Qt::ToolButtonIconOnly</enum>
  </property>
  <widget class="QWidget" name="centralwidget">
   <widget class="QLabel" name="label">
    <property name="geometry">
     <rect>
      <x>30</x>
      <y>30</y>
      <width>611</width>
      <height>41</height>
     </rect>
    </property>
    <property name="font">
     <font>
      <pointsize>18</pointsize>
     </font>
    </property>
    <property name="text">
     <string>Добро пожаловать в &quot;МАСАНАБОР&quot;</string>
    </property>
   </widget>
   <widget class="QPushButton" name="reg_btn">
    <property name="geometry">
     <rect>
      <x>130</x>
      <y>340</y>
      <width>391</width>
      <height>81</height>
     </rect>
    </property>
    <property name="font">
     <font>
      <pointsize>17</pointsize>
     </font>
    </property>
    <property name="text">
     <string>Регистрация</string>
    </property>
   </widget>
   <widget class="QPushButton" name="login_btn">
    <property name="geometry">
     <rect>
      <x>130</x>
      <y>240</y>
      <width>391</width>
      <height>81</height>
     </rect>
    </property>
    <property name="font">
     <font>
      <pointsize>17</pointsize>
     </font>
    </property>
    <property name="text">
     <string>Вход</string>
    </property>
   </widget>
   <widget class="QLineEdit" name="password_line">
    <property name="geometry">
     <rect>
      <x>130</x>
      <y>180</y>
      <width>391</width>
      <height>41</height>
     </rect>
    </property>
    <property name="font">
     <font>
      <pointsize>10</pointsize>
     </font>
    </property>
    <property name="placeholderText">
     <string>Пароль</string>
    </property>
   </widget>
   <widget class="QLineEdit" name="login_line">
    <property name="geometry">
     <rect>
      <x>130</x>
      <y>120</y>
      <width>391</width>
      <height>41</height>
     </rect>
    </property>
    <property name="font">
     <font>
      <pointsize>10</pointsize>
     </font>
    </property>
    <property name="placeholderText">
     <string>Логин</string>
    </property>
   </widget>
   <widget class="QLabel" name="status_lbl">
    <property name="geometry">
     <rect>
      <x>130</x>
      <y>430</y>
      <width>391</width>
      <height>31</height>
     </rect>
    </property>
    <property name="text">
     <string/>
    </property>
   </widget>
  </widget>
  <widget class="QMenuBar" name="menubar">
   <property name="geometry">
    <rect>
     <x>0</x>
     <y>0</y>
     <width>645</width>
     <height>18</height>
    </rect>
   </property>
  </widget>
  <widget class="QStatusBar" name="statusbar"/>
 </widget>
 <resources>
  <include location="lala.qrc"/>
 </resources>
 <connections/>
</ui>
"""
main_template = """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>MainWindow</class>
 <widget class="QMainWindow" name="MainWindow">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>801</width>
    <height>596</height>
   </rect>
  </property>
  <property name="font">
   <font>
    <pointsize>8</pointsize>
   </font>
  </property>
  <property name="windowTitle">
   <string>MainWindow</string>
  </property>
  <widget class="QWidget" name="centralwidget">
   <widget class="QGraphicsView" name="graph">
    <property name="geometry">
     <rect>
      <x>10</x>
      <y>60</y>
      <width>531</width>
      <height>281</height>
     </rect>
    </property>
   </widget>
   <widget class="QLabel" name="label">
    <property name="geometry">
     <rect>
      <x>14</x>
      <y>9</y>
      <width>781</width>
      <height>41</height>
     </rect>
    </property>
    <property name="font">
     <font>
      <pointsize>14</pointsize>
     </font>
    </property>
    <property name="text">
     <string>Добро пожаловать, имя пользователя</string>
    </property>
   </widget>
   <widget class="QDateEdit" name="dateEdit">
    <property name="geometry">
     <rect>
      <x>550</x>
      <y>100</y>
      <width>241</width>
      <height>41</height>
     </rect>
    </property>
    <property name="font">
     <font>
      <pointsize>10</pointsize>
     </font>
    </property>
   </widget>
   <widget class="QDateEdit" name="dateEdit_2">
    <property name="geometry">
     <rect>
      <x>550</x>
      <y>190</y>
      <width>241</width>
      <height>41</height>
     </rect>
    </property>
    <property name="font">
     <font>
      <pointsize>10</pointsize>
     </font>
    </property>
   </widget>
   <widget class="QPushButton" name="watch_btn">
    <property name="geometry">
     <rect>
      <x>550</x>
      <y>270</y>
      <width>241</width>
      <height>41</height>
     </rect>
    </property>
    <property name="font">
     <font>
      <pointsize>10</pointsize>
     </font>
    </property>
    <property name="text">
     <string>Посмотреть график</string>
    </property>
   </widget>
   <widget class="QLabel" name="label_2">
    <property name="geometry">
     <rect>
      <x>554</x>
      <y>59</y>
      <width>231</width>
      <height>31</height>
     </rect>
    </property>
    <property name="font">
     <font>
      <pointsize>8</pointsize>
     </font>
    </property>
    <property name="text">
     <string>С:</string>
    </property>
   </widget>
   <widget class="QLabel" name="label_3">
    <property name="geometry">
     <rect>
      <x>550</x>
      <y>150</y>
      <width>241</width>
      <height>31</height>
     </rect>
    </property>
    <property name="font">
     <font>
      <pointsize>8</pointsize>
     </font>
    </property>
    <property name="text">
     <string>До:</string>
    </property>
   </widget>
   <widget class="QLabel" name="label_4">
    <property name="geometry">
     <rect>
      <x>14</x>
      <y>349</y>
      <width>201</width>
      <height>41</height>
     </rect>
    </property>
    <property name="font">
     <font>
      <pointsize>10</pointsize>
     </font>
    </property>
    <property name="text">
     <string>Калорий сегодня:</string>
    </property>
   </widget>
   <widget class="QLabel" name="label_5">
    <property name="geometry">
     <rect>
      <x>224</x>
      <y>350</y>
      <width>31</width>
      <height>41</height>
     </rect>
    </property>
    <property name="font">
     <font>
      <pointsize>12</pointsize>
     </font>
    </property>
    <property name="text">
     <string>0</string>
    </property>
   </widget>
   <widget class="QPushButton" name="add_btn">
    <property name="geometry">
     <rect>
      <x>10</x>
      <y>520</y>
      <width>231</width>
      <height>41</height>
     </rect>
    </property>
    <property name="font">
     <font>
      <pointsize>8</pointsize>
     </font>
    </property>
    <property name="text">
     <string>Добавить</string>
    </property>
   </widget>
   <widget class="QDateEdit" name="date_add">
    <property name="geometry">
     <rect>
      <x>10</x>
      <y>410</y>
      <width>231</width>
      <height>31</height>
     </rect>
    </property>
   </widget>
   <widget class="QComboBox" name="comboBox">
    <property name="geometry">
     <rect>
      <x>10</x>
      <y>450</y>
      <width>231</width>
      <height>31</height>
     </rect>
    </property>
   </widget>
   <widget class="QLabel" name="label_6">
    <property name="geometry">
     <rect>
      <x>10</x>
      <y>490</y>
      <width>231</width>
      <height>21</height>
     </rect>
    </property>
    <property name="font">
     <font>
      <pointsize>8</pointsize>
     </font>
    </property>
    <property name="text">
     <string>еда - кол-во калорий</string>
    </property>
   </widget>
   <widget class="QLabel" name="label_7">
    <property name="geometry">
     <rect>
      <x>314</x>
      <y>350</y>
      <width>261</width>
      <height>51</height>
     </rect>
    </property>
    <property name="font">
     <font>
      <pointsize>10</pointsize>
     </font>
    </property>
    <property name="text">
     <string> Калорий на день:</string>
    </property>
   </widget>
   <widget class="QSpinBox" name="cal_getter">
    <property name="geometry">
     <rect>
      <x>581</x>
      <y>361</y>
      <width>61</width>
      <height>31</height>
     </rect>
    </property>
    <property name="font">
     <font>
      <pointsize>12</pointsize>
     </font>
    </property>
   </widget>
   <widget class="QPushButton" name="menu_btn">
    <property name="geometry">
     <rect>
      <x>650</x>
      <y>360</y>
      <width>141</width>
      <height>31</height>
     </rect>
    </property>
    <property name="font">
     <font>
      <pointsize>8</pointsize>
     </font>
    </property>
    <property name="text">
     <string>Составить меню</string>
    </property>
   </widget>
   <widget class="QTextBrowser" name="menu">
    <property name="geometry">
     <rect>
      <x>310</x>
      <y>400</y>
      <width>481</width>
      <height>161</height>
     </rect>
    </property>
   </widget>
  </widget>
  <widget class="QMenuBar" name="menubar">
   <property name="geometry">
    <rect>
     <x>0</x>
     <y>0</y>
     <width>801</width>
     <height>18</height>
    </rect>
   </property>
  </widget>
  <widget class="QStatusBar" name="statusbar"/>
 </widget>
 <resources/>
 <connections/>
</ui>
"""


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
                self.status_lbl.setText("Успешная регистрация!")
                time.sleep(1)
                self.start(self.login)
            else:
                self.status_lbl.setText("Длина пароля не может быть меньше 8 символов.")
        else:
            self.status_lbl.setText("Данный логин уже занят.")
        self.con.commit()

    def log_in(self):
        self.login = self.login_line.text()
        self.password = self.password_line.text()
        if not self.cur.execute("SELECT login FROM Accounts WHERE (login=?)",
                                (self.login,)).fetchall():
            self.status_lbl.setText("Данного логина не существует")
        else:
            if self.cur.execute("SELECT password FROM Accounts WHERE (login=? AND password=?)",
                                (self.login, self.password)).fetchall():
                self.status_lbl.setText("Успешный вход!")
                self.start(self.login)
            else:
                self.status_lbl.setText("Неверно введен логин или пароль. Попробуйте еще.")

    def start(self, login):
        self.mn = Main()
        self.mn.show()


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        f = io.StringIO(main_template)
        uic.loadUi(f, self)
        self.add_btn.clicked.connect(self.run)

    def run(self):
        self.label.setText('OK')


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = LoginWidget()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
