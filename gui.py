#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QLabel, QPushButton, QGridLayout, QMessageBox, QWidget
from PyQt5.QtWidgets import QMainWindow, QApplication, QAction, qApp
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore

import numpy as np
import sys

import core

def get_gt_char(gt_num):
    if gt_num < 0:
        return 'M'
    else:
        return str(gt_num)

class MineSweeperWindow(QMainWindow):
    DIFICULTY_SETTINGS = {
        'easy': {
            'shape': (8,8),
            'mine_prob': 0.1,
            'motivational_phrase': 'Easy peasy!',
            # 'motivational_phrase': 'What is this game about, really?',
        },
        'medium': {
            'shape': (14,14),
            'mine_prob': 0.15,
            'motivational_phrase': 'I know you can do it!',
        },
        'hard': {
            'shape': (20,20),
            'mine_prob': 0.2,
            'motivational_phrase': '"It\'s going to be fun!" You said...',
        },
    }

    def __init__(self):
        super().__init__()
        # self.setWindowFlags(self.windowFlags() | QtCore.Qt.CustomizeWindowHint)
        # self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowMaximizeButtonHint)
        # self.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint)

        self.show_truth = False
        self.initUI()
        self.start_new_game()

    def initUI(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('&Game')


        new_game_action = QAction(QIcon(''), '&New Game (Easy)', self)
        # new_game_action.setShortcut('Ctrl+E')
        new_game_action.setShortcuts(['Ctrl+N', 'Ctrl+E'])
        # new_game_action.triggered.connect(self.start_new_game)
        new_game_action.triggered.connect(lambda: self.start_new_game(difficulty='easy'))
        file_menu.addAction(new_game_action)

        new_game_medium_action = QAction(QIcon(''), '&New Game (Medium)', self)
        # new_game_medium_action.setShortcut('Ctrl+E')
        new_game_medium_action.setShortcuts(['Ctrl+M'])
        new_game_medium_action.triggered.connect(lambda: self.start_new_game(difficulty='medium'))
        file_menu.addAction(new_game_medium_action)

        new_game_hard_action = QAction(QIcon(''), '&New Game (Hard)', self)
        # new_game_hard_action.setShortcut('Ctrl+E')
        new_game_hard_action.setShortcuts(['Ctrl+H'])
        new_game_hard_action.triggered.connect(lambda: self.start_new_game(difficulty='hard'))
        file_menu.addAction(new_game_hard_action)

        print_truth_action = QAction(QIcon(''), '&Print Truth (DEBUG)', self)
        print_truth_action.setShortcut('Ctrl+D')
        print_truth_action.triggered.connect(lambda: print(self.mine_sweeper.gt_field, file=sys.stderr))
        file_menu.addAction(print_truth_action)

        swap_action = QAction(QIcon(''), '&Swap Truth and Visible Field', self)
        swap_action.setShortcut('Ctrl+A')
        swap_action.triggered.connect(self.handle_swap)
        file_menu.addAction(swap_action)

        exit_action = QAction(QIcon('exit.png'), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit')
        exit_action.triggered.connect(qApp.quit)
        file_menu.addAction(exit_action)

        self.statusBar()

        # self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('QT Minesweeper')
        self.show()

    def toggle_show_truth(self):
        self.show_truth = not self.show_truth

    def handle_swap(self):
        self.toggle_show_truth()
        self.update_button_labels()

    def start_new_game(self, difficulty='easy'):
        self.show_truth = False
        self.deadly_coordinates = (-1, -1) # The mine the user clicked.

        settings = self.DIFICULTY_SETTINGS[difficulty]
        shape = settings['shape']
        rows, cols = shape

        self.mine_sweeper = core.MineSweeper(shape=shape, mine_prob=settings['mine_prob'])

        # self.setGeometry(rows*20+40, cols*20+40, 250, 150)
        # self.setGeometry(rows*20+40, cols*20+40)

        # self.takeCentralWidget()
        # self.setCentralWidget(None)

        grid = QGridLayout()
        self.cell_buttons = np.empty(shape, dtype=object)
        for r in range(rows):
            for c in range(cols):
                button = QPushButton('X')
                button.setFixedSize(20,20)
                # FIXME: I have no idea why, but without the a first useless kwarg the slot doesn't work.
                #        The first kwarg seems to always be False. But only when called from Qt.
                click_slot = lambda a=None, r=r, c=c: self.cell_button_clicked(r,c)
                right_click_slot = lambda a=None, r=r, c=c: self.cell_button_right_clicked(r,c)
                button.clicked.connect(click_slot)
                # FIXME: This context menu hack works for handling the right button. But it's not the right
                # way, I imagine.
                button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
                button.customContextMenuRequested.connect(right_click_slot)
                # button.setFlat(True)
                grid.addWidget(button, r, c)
                self.cell_buttons[r,c] = button
        central_widget = QWidget(self)
        central_widget.setLayout(grid)
        self.setCentralWidget(central_widget)
        self.update_button_labels()
        self.statusBar().showMessage(settings['motivational_phrase'])
        # print('rows, cols:', rows, cols, file=sys.stderr)
        # print('resizing to:', rows*20+40, cols*20+40, file=sys.stderr)

        # self.resize(rows*20+40, cols*20+40)
        # self.setGeometry(100, 100, rows*20+40, cols*20+40)
        # self.resize(self.sizeHint())
        self.adjustSize() #!# Couldn't make it resize in any way. Until I found this, while desperately searching the docs.

    def update_button_labels(self):
        assert self.cell_buttons.shape == self.mine_sweeper.visible_field.shape
        if self.show_truth:
            peek = self.mine_sweeper.peek_gt
        else:
            peek = self.mine_sweeper.peek_cell
        rows, cols = self.cell_buttons.shape
        for r in range(rows):
            for c in range(cols):
                if self.show_truth:
                    gt_num = self.mine_sweeper.peek_gt(r,c)
                    char = get_gt_char(gt_num)
                else:
                    char = self.mine_sweeper.peek_cell(r,c)
                button = self.cell_buttons[r,c]
                button.setText(char)
                if char == '0':
                    button.setStyleSheet('QPushButton {background-color: none; color: gray;}')
                elif char in '12345678':
                    button.setStyleSheet('QPushButton {background-color: none; color: blue;}')
                elif char in 'F?':
                    button.setStyleSheet('QPushButton {background-color: none; color: orange;}')
                elif char in 'M':
                    if self.deadly_coordinates == (r, c):
                        button.setStyleSheet('QPushButton {background-color: red; color: black;}')
                    else:
                        button.setStyleSheet('QPushButton {background-color: none; color: red;}')
                elif char == 'U': #!# I had forgotten to put back its colors.
                    button.setStyleSheet('QPushButton {background-color: none; color: black;}')
                    # button.setData(0, QtCore.Qt.BackgroundRole, None)

    def check_game_over(self):
        match_progress = self.mine_sweeper.check_match_progress()
        if match_progress == core.MatchProgress.WIN:
            # alert = QMessageBox()
            # alert.setText('YOU WON!')
            # alert.exec_()
            self.statusBar().showMessage('YOU WON!!')
        elif match_progress == core.MatchProgress.DEFEAT:
            # alert = QMessageBox()
            # alert.setText('You lost!')
            # alert.exec_()
            self.statusBar().showMessage('You lost.')

    def cell_button_clicked(self, r, c):
        if core.MatchProgress.INPROGRESS == self.mine_sweeper.check_match_progress():
            self.statusBar().showMessage('')
            revealed_char = self.mine_sweeper.reveal_cell(r, c)
            if revealed_char == 'M':
                self.deadly_coordinates = (r, c)
            self.update_button_labels()
            self.check_game_over()

    def cell_button_right_clicked(self, r, c):
        if core.MatchProgress.INPROGRESS == self.mine_sweeper.check_match_progress():
            self.statusBar().showMessage('')
            self.mine_sweeper.mark_cell(r, c)
            self.update_button_labels()
            self.check_game_over()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MineSweeperWindow()
    sys.exit(app.exec_())