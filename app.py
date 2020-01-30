#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys
import random
import math
import matplotlib
from PySide2.QtCore import Slot
from PySide2.QtGui import QColor

from PySide2.QtWidgets import (QApplication, QHeaderView, QHBoxLayout, QLabel, QLineEdit,
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QVBoxLayout, QWidget, QFileDialog)

from matplotlib.backends.qt_compat import QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)

from matplotlib.figure import Figure
import matplotlib.patches as patches

"""Klasa okienka z wykresem"""
class PlotWidget(QtWidgets.QMainWindow):
    def __init__(self, x, y, route, length, B):
        super().__init__()
        self.xs = x
        self.ys = y
        self.route = route
        self.length = length

        self.B = B

        self.setWindowTitle("Optymalna trasa wrzeciona automatu wiertarskiego")
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)

        canvas = FigureCanvas(Figure(figsize=(10, 10)))
        layout.addWidget(canvas)
        self.addToolBar(NavigationToolbar(canvas, self))
        self._ax = canvas.figure.subplots()



        points = list(zip(self.xs, self.ys))
        for i, txt in enumerate(points):
            if i == 0 or i == len(points) - 1:
                self._ax.annotate("A", txt)
            elif points.count(txt) > 1:
                result = [str(pos) for pos, value in enumerate(points) if value == txt]

                self._ax.annotate(",".join(result), txt)
            else:
                self._ax.annotate(str(i), txt)

        self.xs[:] = [self.xs[self.route[i]] for i in range(len(self.xs))]
        self.ys[:] = [self.ys[self.route[i]] for i in range(len(self.xs))]

        self._ax.plot(self.xs, self.ys, "*-", color="purple")

        self._ax.set_title(
            "Optymalna trasa wrzeciona automatu wiertarskiego\n" + "A-" + "-".join(str(v) for v in route[1:-1]) + "-A\n"
            + "Długość: " + str(round(self.length, 2))

        )
        self._ax.axis([0, max(self.xs) + 1, 0, max(self.ys) + 1])


class Widget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Problem Komiwojażera")

        """Inicjlizacja zmiennych, na których będą dokynowane obliczenia oraz utworzenie obiektów
        (tabela,pola edycyjne,przyciski)"""

        self.x = []
        self.y = []
        self.W = 0

        self.slots_coordinates = QTableWidget()
        self.slots_count = QLineEdit()
        self.A_x = QLineEdit()
        self.A_y = QLineEdit()
        self.B_x = QLineEdit()
        self.B_y = QLineEdit()

        self.file_name = QLineEdit()
        self.from_keys = QPushButton("Wprowadź dane")
        self.random = QPushButton("Generuj losowe wartości")
        self.from_file = QPushButton("Wprowadź dane z pliku")
        self.clear = QPushButton("Wyczyść")
        self.quit = QPushButton("Zamknij")
        self.visualize = QPushButton("Zwizualizuj")

        self.save = QPushButton("Zapis macierz do pliku")

        self.result_text = QLabel("Wartość plecaka:")
        self.result1 = QLabel()
        self.result2 = QLabel()

        """Tworzenie layoutów a następnie dodawanie do nich widgetów"""

        self.left = QVBoxLayout()
        self.left.addWidget(QLabel("Ilość otworów"))
        self.left.addWidget(self.slots_count)
        self.left.addWidget(QLabel("Współrzędne prostokąta"))
        self.left.addWidget(QLabel("Współrzędne A"))
        self.left.addWidget(self.A_x)
        self.left.addWidget(self.A_y)
        self.left.addWidget(QLabel("Współrzędne B"))
        self.left.addWidget(self.B_x)
        self.left.addWidget(self.B_y)
        self.left.addWidget(self.from_keys)
        self.left.addWidget(self.random)
        self.left.addWidget(self.from_file)
        self.left.addWidget(self.clear)
        self.left.addWidget(self.quit)
        self.center = QVBoxLayout()
        self.right = QVBoxLayout()
        """Tworzenie  głównego layoutu a następnie dodawanie do nich trzech utworzonych wcześniej"""
        self.layout = QHBoxLayout()
        self.layout.addLayout(self.left)
        self.layout.addLayout(self.center)
        self.layout.addLayout(self.right)

        self.setLayout(self.layout)

        """Komunikacja pomiędzy obiektami"""
        self.from_keys.clicked.connect(self.create_table)

        self.random.clicked.connect(self.create_table)
        self.random.clicked.connect(self.random_values)

        self.from_file.clicked.connect(self.create_table)
        self.from_file.clicked.connect(self.values_from_file)

        self.visualize.clicked.connect(self.get_plot)

        self.slots_count.textChanged[str].connect(self.check_disable)

        for item in [self.A_x, self.A_y, self.B_x, self.B_y]:
            item.textChanged[str].connect(self.check_disable)

        self.clear.clicked.connect(self.clear_table)
        self.save.clicked.connect(self.save_to_file)
        self.quit.clicked.connect(self.quit_application)

    """Dodawanie do layoutu przycisków umożliwiających wybór metody obliczeń, zapisu do pliku oraz tekstu z wynikami"""

    def create_right_layout(self):

        self.layout.addLayout(self.right)
        self.right.addWidget(self.visualize)

        self.right.addWidget(self.save)
        self.right.addWidget(self.result_text)
        self.right.addWidget(self.result1)
        self.right.addWidget(self.result2)
        self.result_text.hide()
        self.result1.hide()  # wyniki ukryte dopóki użytkownik nie zażąda rozwiązania
        self.result2.hide()

    """Tworzenie tabeli o ilości kolumn n, podanych przez użytkownika"""

    @Slot()
    def create_table(self):
        self.slots_coordinates.setColumnCount(int(self.slots_count.text()))
        self.slots_coordinates.setRowCount(2)
        self.slots_coordinates.setVerticalHeaderLabels(["x", "y"])

        self.slots_coordinates.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.slots_coordinates.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.center.addWidget(self.slots_coordinates)
        self.create_right_layout()

    """Uzupełnianie pustych wartości obiektowej tabeli wartościami losowymi, konwertując te liczby na string, aby dane
           były poprawnie wyświetlone w oknie"""

    @Slot()
    def random_values(self):

        for i in range(self.slots_coordinates.columnCount()):
            self.slots_coordinates.setItem(0, i, QTableWidgetItem(
                str(random.randint(int(self.A_x.text()), int(self.B_x.text())))))
            self.slots_coordinates.setItem(1, i, QTableWidgetItem(
                str(random.randint(int(self.A_y.text()), int(self.B_y.text())))))

    """Uzupełnianie obiektowej tabeli wartościami z pliku"""

    @Slot()
    def values_from_file(self):
        self.left.insertWidget(9, self.file_name)  # dodawanie widgetu,który będzie wyświetlał nazwę pliku
        self.file_name.setText(QFileDialog.getOpenFileName()[0])

        with open(self.file_name.text(), 'r') as f:
            for idx_line, line in enumerate(f):
                for idx, item in enumerate(line.split(' ')):
                    self.slots_coordinates.setItem(idx_line, idx, QTableWidgetItem(str(item)))

    """Zapisywanie tabeli do pliku"""

    @Slot()
    def save_to_file(self):

        self.file_name.setText(QFileDialog.getSaveFileName()[0])

        with open(self.file_name.text(), 'w') as f:
            for i in range(self.slots_coordinates.columnCount()):
                f.write(self.slots_coordinates.item(0, i).text() + ' ')
            f.write('\n')
            for j in range(self.slots_coordinates.columnCount()):
                f.write(self.slots_coordinates.item(1, j).text() + ' ')

    """Konwertowanie obiektowej tabeli na listy p i w, na której będą dokonywane obliczenia"""

    def convert_to_lists(self):
        self.x.append(int(self.A_x.text()))
        self.y.append(int(self.A_y.text()))
        for i in range(self.slots_coordinates.columnCount()):
            self.x.append(int(self.slots_coordinates.item(0, i).text()))
        for j in range(self.slots_coordinates.columnCount()):
            self.y.append(int(self.slots_coordinates.item(1, j).text()))

    """Tworzenie macierzy odległości"""

    def create_matrix(self):
        slots_count = int(self.slots_count.text())
        self.matrix = [[0.0] * (slots_count + 1) for i in range(slots_count + 1)]

        for i in range(slots_count + 1):
            for j in range(slots_count + 1):
                self.matrix[i][j] = math.sqrt((self.x[i] - self.x[j]) ** 2 + (self.y[i] - self.y[j]) ** 2)
            self.matrix[i][i] = -math.inf
        return self.matrix

    @Slot()
    def get_plot(self):

        self.convert_to_lists()

        print("Stworzona macierz odległości:",self.create_matrix())

        self.algorytm()

    """Algorytm rozwiązujący problem Komiwojażera"""
    def algorytm(self):
        first_row = self.matrix[0]

        route = [0, 0]
        copy_matrix = [row[:] for row in self.matrix]

        for j in range(len(self.matrix) - 1):
            #print(first_row)
            #znajdowanie indeksu maksymalnej wartości z pierwszego wiersza
            idx_max = first_row.index(max(first_row))

            chosen = []
            # obliczenia dotyczące wyboru najbardziej optrymalnej trasy
            if len(route)>2:
                for i in range(len(route) - 1):
                    prop = copy_matrix[route[i]][idx_max] + copy_matrix[idx_max][route[i + 1]] - copy_matrix[route[i]][route[i + 1]]
                    chosen.append(prop)
                idx_chosen = chosen.index(min(chosen))
            else:
                idx_chosen=0


            # dodanie wybrane punktu do trasy

            route.insert(idx_chosen+1 , idx_max)
            #print(idx_chosen + 1, "-", idx_max)

            # sprawdzenie czy wartosci nie są większe od wiersza idx_max, jeśli tak przypisanie wartości z macierzy do first_row
            for idx in range(len(copy_matrix)-1) :
                if copy_matrix[idx_max][idx] < first_row[idx]:
                    first_row[idx] = copy_matrix[idx_max][idx]
            first_row[idx_max] = -math.inf
        # długość trasy
        sum = 0
        for i in range(len(route) - 1):
            sum += copy_matrix[route[i]][route[i + 1]]

        self.x.append(int(self.A_x.text()))
        self.y.append(int(self.A_y.text()))
        B = (int(self.B_x.text()), int(self.B_y.text()))
        PlotWidget(self.x, self.y, route, sum, B).show()

    """Funkcja sprawdza czy są wpisane wartości 
        jeśli nie, niemożliwe jest wygenerowanie tabeli"""

    @Slot()
    def check_disable(self):
        actions = [self.from_keys, self.random, self.from_file]
        for action in actions:
            if not self.slots_count.text() or not self.A_x.text() or not self.A_y.text() or not self.B_x.text() or not self.B_y.text():
                action.setEnabled(False)
            else:
                action.setEnabled(True)

    """Zerowanie zmiennej przechowującej wynik, oraz usuwanie wartości w tablciach p i w
    w celu wykonania drugiej metody do rozwiązania algorytmu plecakowego"""

    def clear_result(self):
        self.W = 0
        self.x = []
        self.y = []

    """Czyszczenie tabeli, czyli usuwanie kolumn, i ustawienie dwu wierszy, usuwanie wartosći tablic p,q,
         odblokawanie przycisków do rozwiązania problemu oraz ukrywanie pól z wynikami
         w celu możliwości pracy na innych danych"""

    @Slot()
    def clear_table(self):
        self.slots_coordinates.setColumnCount(0)
        self.slots_coordinates.setRowCount(2)
        self.x = []
        self.y = []

        self.result1.hide()
        self.result2.hide()
        self.result_text.hide()

    @Slot()
    def quit_application(self):
        QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = Widget()
    widget.resize(1200, 300)
    widget.show()
    sys.exit(app.exec_())
