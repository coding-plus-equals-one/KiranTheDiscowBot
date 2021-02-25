#!/usr/bin/env python3

class Mark:
    def __init__(self, is_x, move_num):
        self.is_x = is_x
        self.move_num = move_num

class Box:
    def __init__(self):
        self._marks = []
        self._big_mark = None

    def add_mark(self, mark):
        self._marks.append(mark)

class Board:
    def __init__(self):
        self._boxes = [Box() for _ in range(9)]

    def add_mark(self, location, mark):
        self._boxes[location].add_mark(mark)
