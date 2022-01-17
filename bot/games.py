from .users import *
from .enums import Direction

import random
import json

class Game2048(object):
	def __init__(self) -> None:
		self.screen = [
			[0, 0, 0, 0],
			[0, 0, 0, 0],
			[0, 0, 0, 0],
			[0, 0, 0, 0]
		]

		self.points = 0
	
	def FormatKeyboard(self) -> str:
		btns = [
			[
				{
					"action":{  
						"type":"callback",
						"payload": {
							'ktype': 'game2048',
							'btype': 'block',
							'payload': {
								'blockI': blockI,
								'lineI': lineI
							}
						},
						"label": self.screen[lineI][blockI]
					},
					"color":
					"secondary" if self.screen[lineI][blockI] == 0 else
					"primary"
				}
				for blockI in range(0, self.screen[lineI].__len__())
			]
			for lineI in range(0, self.screen.__len__())
		]
		btns.append([
			{
				"action":{  
					"type":"callback",
					"payload": {
						'ktype': 'game2048',
						'btype': 'move',
						'payload': {
							'dir': Direction.Left
						}
					},
					"label":"⬅"
				},
				"color":"secondary"
			},
			{
				"action":{  
					"type":"callback",
					"payload": {
						'ktype': 'game2048',
						'btype': 'move',
						'payload': {
							'dir': Direction.Up
						}
					},
					"label":"⬆"
				},
				"color":"secondary"
			},
			{
				"action":{  
					"type":"callback",
					"payload": {
						'ktype': 'game2048',
						'btype': 'move',
						'payload': {
							'dir': Direction.Down
						}
					},
					"label":"⬇"
				},
				"color":"secondary"
			},
			{
				"action":{  
					"type":"callback",
					"payload": {
						'ktype': 'game2048',
						'btype': 'move',
						'payload': {
							'dir': Direction.Right
						}
					},
					"label":"➡"
				},
				"color":"secondary"
			},
			{
				"action":{  
					"type":"callback",
					"payload": {
						'ktype': 'game2048',
						'btype': 'exit',
						'payload': {}
					},
					"label":"назад"
				},
				"color":"secondary"
			}
		])

		keyboard = {
			"one_time": False,
			"inline": False,
			"buttons": btns
		}
		return json.dumps(keyboard)
	
	def Clear(self):
		self.screen = [
			[0, 0, 0, 0],
			[0, 0, 0, 0],
			[0, 0, 0, 0],
			[0, 0, 0, 0]
		]
	
	def Random(self) -> bool:
		randoms = []
		lineI = 0
		for line in self.screen:
			blockI = 0
			for block in line:
				if block == 0:
					randoms.append((lineI, blockI))
				blockI += 1
			lineI += 1

		if randoms.__len__() == 0:
			return False

		maxI = randoms.__len__() - 1
		random.seed()
		first = round(random.random() * maxI)
		if randoms.__len__() == 1:
			lineI, blockI = randoms[first]
			self.screen[lineI][blockI] = 2
			return True
		random.seed()
		second = round(random.random() * maxI)

		if first == second: return self.Random()

		lineI, blockI = randoms[first]
		random.seed()
		self.screen[lineI][blockI] = 2 if random.random() <= 0.9 else 4 # 10% chance to cell with 4
		random.seed()
		lineI, blockI = randoms[second]
		self.screen[lineI][blockI] = 2 if random.random() <= 0.9 else 4
		return True

	def MoveLeft(self) -> bool:
		moved = False
		lineI = 0
		for line in self.screen:
			blockI = 0
			for block in line:
				if blockI == 0 or block == 0: 
					blockI += 1
					continue
				
				blockOffset = 1
				while (blockI - blockOffset) >= 0:
					i = blockI - blockOffset
					blockForCheck = line[i]
					if blockForCheck == 0:
						if i == 0:
							self.screen[lineI][blockI] = 0
							self.screen[lineI][i] = block
							moved = True
							break
						blockOffset += 1
						continue
					else:
						self.screen[lineI][blockI] = 0	
						if blockForCheck == block:
							self.screen[lineI][i] = block * 2
							self.points += block * 2
							moved = True
						else:
							self.screen[lineI][i+1] = block
							moved = moved or (i+1 != blockI)
						break
				blockI += 1
			lineI += 1
		return moved
	def MoveUp(self) -> bool:
		moved = False
		for blockI in range(0, self.screen[0].__len__()):
			for lineI in range(0, self.screen.__len__()):
				line = self.screen[lineI]
				block = line[blockI]
				
				if lineI == 0 or block == 0: 
					continue
				
				lineOffset = 1
				while (lineI - lineOffset) >= 0:
					i = (lineI - lineOffset)
					_line = self.screen[i]
					blockForCheck = _line[blockI]

					if blockForCheck == 0:
						if i == 0:
							self.screen[lineI][blockI] = 0
							self.screen[i][blockI] = block
							moved = True
							break
						lineOffset += 1
						continue
					else:
						self.screen[lineI][blockI] = 0
						if blockForCheck == block:
							self.screen[i][blockI] = block * 2
							self.points += block * 2
							moved = True
						else: 
							self.screen[i+1][blockI] = block
							moved = moved or (i+1 != lineI)
						break
		return moved
	def MoveDown(self) -> bool:
		moved = False
		for blockI in range(0, self.screen[0].__len__()):
			for lineI in range(0, self.screen.__len__()):
				lineI = self.screen.__len__() - lineI - 1

				line = self.screen[lineI]
				block = line[blockI]
				
				if lineI == self.screen.__len__() - 1 or block == 0: 
					continue
				
				lineOffset = 1
				while (lineI + lineOffset) <= self.screen.__len__() - 1:
					i = (lineI + lineOffset)
					_line = self.screen[i]
					blockForCheck = _line[blockI]

					if blockForCheck == 0:
						if i == self.screen.__len__() - 1:
							self.screen[lineI][blockI] = 0
							self.screen[i][blockI] = block
							moved = True
							break
						lineOffset += 1
						continue
					else:
						self.screen[lineI][blockI] = 0
						if blockForCheck == block:
							self.screen[i][blockI] = block * 2
							self.points += block * 2
							moved = True
						else: 
							self.screen[i-1][blockI] = block
							moved = moved or (i-1 != lineI)
						break
		return moved
	def MoveRight(self) -> bool:
		moved = False
		lineI = 0
		for line in self.screen:
			for blockI in range(0, line.__len__()):
				blockI = line.__len__() - blockI - 1
				block = line[blockI]

				if blockI == line.__len__() - 1 or block == 0:
					continue
				
				blockOffset = 1
				while (blockI + blockOffset) < line.__len__():
					i = blockI + blockOffset
					blockForCheck = line[i]
					if blockForCheck == 0:
						if i == (line.__len__() - 1):
							self.screen[lineI][blockI] = 0
							self.screen[lineI][i] = block
							moved = True
							break
						blockOffset += 1
						continue
					else:
						self.screen[lineI][blockI] = 0	
						if blockForCheck == block:
							self.screen[lineI][i] = block * 2
							self.points += block * 2
							moved = True
						else: 
							self.screen[lineI][i-1] = block
							moved = moved or (i-1 != blockI)
						break
			lineI += 1
		return moved
	
	def Move(self, direction: Direction) -> bool:
		return getattr(self, 'Move' + str(Direction._find_value_path(direction)))()
	
	def IsMovesAvailable(self) -> bool:
		for lineI in range(0, self.screen.__len__()):
			line = self.screen[lineI]
			for blockI in range(0, line.__len__()):
				block = line[blockI]
				if\
					block == 0 or\
					(line[blockI - 1] == 0 if blockI != 0 else False) or\
					(line[blockI + 1] == 0 if blockI != line.__len__() - 1 else False) or\
					(line[blockI - 1] == block if blockI != 0 else False) or\
					(line[blockI + 1] == block if blockI != line.__len__() - 1 else False) or\
					(self.screen[lineI - 1][blockI] == 0 if lineI != 0 else False) or\
					(self.screen[lineI + 1][blockI] == 0 if lineI != self.screen.__len__() - 1 else False) or\
					(self.screen[lineI - 1][blockI] == block if lineI != 0 else False) or\
					(self.screen[lineI + 1][blockI] == block if lineI != self.screen.__len__() - 1 else False):
					return True
		return False