import random
from .items import *

THI_EASY = 0
THI_MIDDLE = 1
THI_HARD = 2

ThiefHouses = [
	[ # Easy
		{
			'thumbnail': 'placeholder13x8.png',
			'name': 'Лёгкий(!!!PLACEHOLDER!!!)',
			'id': 'easy1',
			'difficult_rus': 'Лёгкий',
			'drop': [
				Item('none', 'DUMMY ITEM0'),
				Item('none', 'DUMMY ITEM1'),
				Item('none', 'DUMMY ITEM2'),
				Item('none', 'DUMMY ITEM3')
			]
		}
	],
	[ # Middle
		{
			'thumbnail': 'placeholder13x8.png',
			'name': 'Средний(!!!PLACEHOLDER!!!)',
			'id': 'middle1',
			'difficult_rus': 'Средний',
			'drop': [
				Item('none', 'DUMMY ITEM0'),
				Item('none', 'DUMMY ITEM1'),
				Item('none', 'DUMMY ITEM2'),
				Item('none', 'DUMMY ITEM3')
			]
		}
	],
	[ # Hard
		{
			'thumbnail': 'placeholder13x8.png',
			'name': 'Сложный(!!!PLACEHOLDER!!!)',
			'id': 'hard1',
			'difficult_rus': 'Сложный',
			'drop': [
				Item('none', 'DUMMY ITEM0'),
				Item('none', 'DUMMY ITEM1'),
				Item('none', 'DUMMY ITEM2'),
				Item('none', 'DUMMY ITEM3')
			]
		}
	]
]


def RandomThiefHouse_Easy():
	lst = ThiefHouses[THI_EASY]
	random.seed()
	i = round(random.random() * (lst.__len__() - 1))
	return lst[i]

def RandomThiefHouse_Middle():
	lst = ThiefHouses[THI_MIDDLE]
	random.seed()
	i = round(random.random() * (lst.__len__() - 1))
	return lst[i]

def RandomThiefHouse_Hard():
	lst = ThiefHouses[THI_HARD]
	random.seed()
	i = round(random.random() * (lst.__len__() - 1))
	return lst[i]


def RandomThiefHouses():
	return [RandomThiefHouse_Easy(), RandomThiefHouse_Middle(), RandomThiefHouse_Hard()]