#!/usr/bin/env python

from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton, QGridLayout, QMessageBox
from PyQt5 import QtCore

import numpy as np
import sys

import core

"""
TODO: Do it more like this: https://stackoverflow.com/questions/4838890/python-pyqt-popup-window
"""

def button_clicked(*args):
	print('clicked', *args)

# class CellButton(QPushButton):
#     def __init__(self):
#         super(MyWidget, self).__init__()
#         self.installEventFilter(self)

#     def eventFilter(self, QObject, event):
#         if event.type() == QEvent.MouseButtonPress:
#             if event.button() == Qt.LeftButton:
#             if event.button() == Qt.RightButton:
#                 print("Right button clicked")
#         return False

def update_button_labels(cell_buttons, mine_sweeper):
	assert cell_buttons.shape == mine_sweeper.visible_field.shape
	rows, cols = cell_buttons.shape
	for r in range(rows):
		for c in range(cols):
			char = mine_sweeper.peek_cell(r,c)
			button = cell_buttons[r,c]
			button.setText(char)
			if char == '0':
				button.setStyleSheet('QPushButton {color: gray;}')
			elif char in '12345678':
				button.setStyleSheet('QPushButton {color: blue;}')
			elif char in 'F?':
				button.setStyleSheet('QPushButton {color: orange;}')
			elif char in 'M':
				button.setStyleSheet('QPushButton {background-color: red;}')
				# button.setStyleSheet('QPushButton {backcolor: orange;}')


def check_game_over(mine_sweeper):
	match_progress = mine_sweeper.check_match_progress()
	if match_progress == core.MatchProgress.WIN:
		alert = QMessageBox()
		alert.setText('YOU WON!')
		alert.exec_()
	elif match_progress == core.MatchProgress.DEFEAT:
		alert = QMessageBox()
		alert.setText('You lost!')
		alert.exec_()

def cell_button_clicked(cell_buttons, mine_sweeper, r, c):
	mine_sweeper.reveal_cell(r, c)
	update_button_labels(cell_buttons, mine_sweeper)
	check_game_over(mine_sweeper)

def cell_button_right_clicked(cell_buttons, mine_sweeper, r, c):
	mine_sweeper.mark_cell(r, c)
	update_button_labels(cell_buttons, mine_sweeper)
	check_game_over(mine_sweeper)

def main():
	shape = (10, 10)
	rows, cols = shape

	mine_sweeper = core.MineSweeper(shape=shape)

	app = QApplication([])
	window = QWidget()
	grid = QGridLayout()
	cell_buttons = np.empty(shape, dtype=object)
	for r in range(rows):
		for c in range(cols):
			button = QPushButton('X')
			button.setFixedSize(20,20)
			# FIXME: I have no idea why, but without the a first useless kwarg the slot doesn't work.
			#        The first kwarg seems to always be False. But only when called from Qt.
			click_slot = lambda a=None, r=r, c=c: cell_button_clicked(cell_buttons, mine_sweeper, r,c)
			right_click_slot = lambda a=None, r=r, c=c: cell_button_right_clicked(cell_buttons, mine_sweeper, r,c)
			button.clicked.connect(click_slot)
			# FIXME: This context menu hack works for handling the right button. But it's not the right
			# way, I imagine.
			button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
			button.customContextMenuRequested.connect(right_click_slot)
			grid.addWidget(button, r, c)
			cell_buttons[r,c] = button
			# if r==9 and c==9:
			# 	click_slot()
	update_button_labels(cell_buttons, mine_sweeper)
	window.setLayout(grid)
	window.show()
	app.exec_()


if __name__ == '__main__':
	main()
