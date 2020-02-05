#!/usr/bin/env python

import argparse
import sys
import re

import core

COMMAND_RE = re.compile(r'\s*(?P<action>[rufRUF?])?\s*(?P<i>\d+)\s*[ ,]\s*(?P<j>\d+)\s*()\s*(?P<action_post>[rufRUF?])?')
PRINT_FIELD_MAP = {
	'M': '*',
	'U': '.',
	'F': 'P',
}

PRINT_GT_MAP = {
	-1: '*',
}

HELP_MESSAGE_COMMANDS = """
The command should be formated like so: '<ACTION> <ROW> <COL> <ACTION>' (without quotes, and you choose whether to put the action on the beggining or the end). Where you replace <ROW> with the row number of the cell you're acting on, <COL> with the column, and <ACTION> with one of the following actions:
 - 'r' to reveal the cell. If there are any mines on that cell they will explode on your face.
 - 'f' to mark it with a flag.
 - 'u' to unmark it.
 - "?" to mark it as dubious, i.e., you don't know if there is really a bomb in there.
""".strip()

def print_field(minesweeper, gt=False):
	rows, cols = minesweeper.shape

	s = ''

	# Header.
	col_width = max( len(str(c)) for c in range(cols) )
	row_width = max( len(str(r)) for r in range(rows) )
	col_formatter = '{: <'+str(col_width)+'}'
	row_formatter = '{: <'+str(row_width)+'}'
	column_idxs = [ col_formatter.format(c) for c in range(cols) ]
	header_offset = ' ' * (row_width+1)
	column_idxs_str = ' '.join(column_idxs)

	s += header_offset + column_idxs_str + '\n'
	s += header_offset + '-'*len(column_idxs_str) + '\n'
	for r in range(rows):
		s += row_formatter.format(r) + '|'
		for c in range(cols):
			if gt:
				value = minesweeper.peek_gt(r,c)
				if value in PRINT_GT_MAP:
					char = PRINT_GT_MAP[value]
				else:
					char = str(value)
			else:
				char = minesweeper.peek_cell(r,c)
				if char in PRINT_FIELD_MAP:
					char = PRINT_FIELD_MAP[char]
			s += char
			if c == (cols-1):
				s += ' ' * (col_width-1)
			else:
				s += ' ' * (col_width)
		s += '|' + row_formatter.format(r) + '\n'
	s += header_offset + '-'*len(column_idxs_str) + '\n'
	s += header_offset + column_idxs_str + '\n'

	print(s)

def main():
	args = parse_args()

	if args.seed is not None:
		core.set_seed(args.seed)

	minesweeper = core.MineSweeper(shape=(args.n_rows, args.n_cols), mine_prob=args.difficulty)

	while minesweeper.check_match_progress() == core.MatchProgress.INPROGRESS:
		print()
		print_field(minesweeper)
		command = input('Command: ')
		match = COMMAND_RE.match(command)
		if match:
			cmd = match.groupdict()
			action = cmd['action_post'] if cmd['action'] is None else cmd['action']
			cell_tuple = (int(cmd['i']),int(cmd['j']))
			if action == None or action.upper() == 'R':
				minesweeper.reveal_cell(*cell_tuple)
			else:
				minesweeper.mark_cell(*cell_tuple, mark=action.upper())
		else:
			print(f'Invalid command `{command}`.')
			print(HELP_MESSAGE_COMMANDS)

	print()
	print_field(minesweeper)

	match_progress = minesweeper.check_match_progress()
	if match_progress == core.MatchProgress.WIN:
		msg = '== YOU WON =='
		print('='*len(msg))
		print(msg)
		print('='*len(msg))
	else:
		print('Game Over. You lose.')

		print()
		print_field(minesweeper, gt=True)

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('-c', '--n-cols', type=int, default=10)
	parser.add_argument('-r', '--n-rows', type=int, default=10)
	parser.add_argument('-p', '--difficulty', type=float, default=0.1)
	parser.add_argument('-s', '--seed', type=int)
	args = parser.parse_args()
	return args

if __name__ == '__main__':
	main()
