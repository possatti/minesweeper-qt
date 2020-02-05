#!/usr/bin/env python

from enum import Enum

import numpy as np
import sys

NEIGHBOR_OFFSETS = np.array([
	[-1,-1,-1, 0, 0, 1, 1, 1],
	[-1, 0, 1,-1, 1,-1, 0, 1],
])
MARKABLE_CELLS = ['U', 'F', '?']

MatchProgress = Enum('MatchProgress', 'INPROGRESS DEFEAT WIN')

def set_seed(seed):
	np.random.seed(seed)

def create_field(shape=(5,5), mine_prob=0.1):
	"""Create a minesweeper field.

	The field is a 2D numpy array, where mines are `-1`, and numbers from 0 to 8
	represent free cells and indicate how many mines are surrounding it.

	Args:
		shape: integer tuple (height, width) describing the dimensions of the field.
		mine_prob: probability a cell contains a mine. $0<p<1$
	"""
	mines = np.random.choice([0, 1], shape, p=[1-mine_prob, mine_prob])
	mines_padded = np.pad(mines, 1, mode='constant', constant_values=0)
	inds_i, inds_j = np.indices(shape)
	counts = np.zeros(shape)
	for i_offset, j_offset in zip(*NEIGHBOR_OFFSETS):
		take_inds_i = inds_i + 1 + i_offset
		take_inds_j = inds_j + 1 + j_offset
		counts += mines_padded[take_inds_i, take_inds_j]
	field = counts.copy()
	field[mines==1] = -1
	field = field.astype(np.int8)

	return field


class MineSweeper:
	"""Main class that controls a minesweeper game."""
	def __init__(self, shape=(10,10), mine_prob=0.1):
		self.restart(shape=shape, mine_prob=mine_prob)

	def restart(self, shape=(10,10), mine_prob=0.1):
		shape = np.array(shape)
		self.shape = shape
		self.n, self.m = shape
		self.gt_field = create_field(shape=shape, mine_prob=mine_prob)
		self.visible_field = np.repeat('U', shape.prod()).reshape(shape)
		# Meaning of values on the visible field:
		#  - 'U': Unrevealed
		#  - 'M': Mine (Boom! Game over.)
		#  - 'F': Flag
		#  - '?': Doubt
		#  - '[0-8]': number of mines surrounding this free cell.

	def reveal_cell(self, i, j, mask='U'):
		if i < 0 or i >= self.n:
			return
		if j < 0 or j >= self.m:
			return
		gt_value = self.gt_field[i, j]
		vis_value = self.visible_field[i, j]
		if vis_value in mask:
			if gt_value > 0:
				self.visible_field[i, j] = str(gt_value)
			elif gt_value == 0:
				self.visible_field[i, j] = str(gt_value)
				for i_offset, j_offset in zip(*NEIGHBOR_OFFSETS):
					self.reveal_cell(i+i_offset,j+j_offset, mask='UF?')
			else:
				# BOOM!
				self.visible_field[i, j] = 'M'
		return self.visible_field[i, j]

	def peek_gt(self, i, j):
		return self.gt_field[i,j]

	def peek_cell(self, i, j):
		return self.visible_field[i,j]

	def mark_cell(self, i, j, mark=None):
		cell_value = self.visible_field[i, j]
		if cell_value in MARKABLE_CELLS:
			if mark is None:
				idx = MARKABLE_CELLS.index(cell_value)
				new_idx = (idx+1) % len(MARKABLE_CELLS)
				new_mark = MARKABLE_CELLS[new_idx]
				self.visible_field[i, j] = new_mark
			else:
				assert mark in MARKABLE_CELLS
				self.visible_field[i, j] = mark
		else:
			raise ValueError(f'Cell does not contain a markable value. Got `{cell_value}`.')

	def check_win(self):
		all_mines_flagged_correctly = ((self.visible_field=='F') == (self.gt_field==-1)).all()
		all_expanded_or_marked = not np.isin(self.visible_field, ['U','M','?']).any()
		return all_mines_flagged_correctly and all_expanded_or_marked

	def check_defeat(self):
		return (self.visible_field == 'M').any()

	def check_match_progress(self):
		if self.check_defeat():
			return MatchProgress.DEFEAT
		elif self.check_win():
			return MatchProgress.WIN
		else:
			return MatchProgress.INPROGRESS
