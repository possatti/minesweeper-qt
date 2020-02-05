#!/usr/bin/env python

from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette

def example1():
	app = QApplication([])
	label = QLabel('Hello World!')
	label.show()
	app.exec_()

def example2():
	app = QApplication([])
	app.setStyle('Windows') # Default: Fusion
	from PyQt5.QtCore import Qt
	from PyQt5.QtGui import QPalette
	palette = QPalette()
	palette.setColor(QPalette.ButtonText, Qt.red)
	app.setPalette(palette)
	window = QWidget()
	layout = QVBoxLayout()
	top_button = QPushButton('Top')
	bottom_button = QPushButton('Bottom')
	layout.addWidget(top_button)
	layout.addWidget(bottom_button)
	window.setLayout(layout)
	window.show()
	app.exec_()

def example3():
	app = QApplication([])
	button = QPushButton('Click')
	def on_button_clicked():
	    alert = QMessageBox()
	    alert.setText('You clicked the button!')
	    alert.exec_()

	button.clicked.connect(on_button_clicked)
	button.show()
	app.exec_()

example3()
