import copy
import numpy as np
import os
import re
import requests

from typing import Self, Iterable

class Binairo:
    def __init__(self, puzzle: str | os.PathLike | Self):
        if isinstance(puzzle, Binairo):
            self.puzzle = puzzle.puzzle
            self.size = puzzle.size
        
        elif isinstance(puzzle, str):
            if os.path.exists(puzzle):
                with open(puzzle, "r") as f:
                    puzzle = f.read().replace("\n", "")
            
            l = len(puzzle)
            k = int(l ** 0.5)
            if k ** 2 != l:
                raise ValueError("Invalid puzzle size")
            
            self.size = k
            self.puzzle = puzzle
        
        else:
            raise TypeError("Invalid type for puzzle")
        
        self.possible_rows = self._determine_possible_lines(self.size)
        self.possible_columns = copy.deepcopy(self.possible_rows)
    
    def __str__(self):
        return self.__repr__()
    
    def __getitem__(self, key: int | slice | tuple[int | slice, int | slice]) -> str:
        if isinstance(key, tuple):
            if len(key) != 2:
                raise IndexError("Invalid index for 2D array")
            
            key_r, key_c = key

            return "".join([self.puzzle[i*self.size:(i+1)*self.size][key_c] for i in range(self.size)][key_r])
        
        if isinstance(key, (int, slice)):
            return "".join([self.puzzle[i*self.size:(i+1)*self.size] for i in range(self.size)][key])
        
        raise TypeError("Invalid key type")
    
    def __setitem__(self, key: tuple[int, int], value: str):
        if len(value) != 1:
            raise ValueError("Invalid length for value")
        
        if isinstance(key, tuple):
            key1, key2 = key
            index = key1 * self.size + key2
            self.puzzle = self.puzzle[:index] + value + self.puzzle[index + 1:]
            return
            
        raise TypeError("Invalid key type")
    
    def _setrow(self, index: int, value: str):
        if len(value) != self.size:
            raise ValueError("Invalid length for value")
        
        self.puzzle = self.puzzle[:index * self.size] + value + self.puzzle[(index + 1) * self.size:]

    def _setcolumn(self, index: int, value: str):
        if len(value) != self.size:
            raise ValueError("Invalid length for value")
        
        self.puzzle = "".join([value[i] for i in range(self.size) for j in range(self.size) if j == index])
    
    def _getcolumn(self, index: int) -> str:
        return self.puzzle[index::self.size]
    
    def _getrow(self, index: int) -> str:
        return self.puzzle[index * self.size:(index + 1) * self.size]
    
    def _determine_possible_lines(self, size: int) -> np.ndarray:
        """Determine the possible arrays for a given size.
        
        This will generate all strings that are a possible solution for a row or column.
        """
        arrays = []
        for i in range(2 ** size):
            solution = f"{i:0{size}b}"
            if "000" in solution or "111" in solution:
                continue

            if solution.count("0") != size // 2:
                continue

            arrays.append(np.array([int(c) for c in solution]))
        
        return np.array(arrays)
    
    def _get_solutions(self, line: str, possible_lines: list[np.ndarray]) -> np.ndarray:
        """Get all possible solutions for a given line.
        
        This will return a list of all possible solutions for a given line.
        """
        array = np.array([int(c) for c in line.replace("X", "2")])
        zeroes = array == 0
        ones = array == 1
        return np.array([solution for solution in possible_lines if np.all(solution[zeroes] == 0) and np.all(solution[ones] == 1)])
    
    def _check_row(self, row: int) -> list[int]:
        """Compare possible options for given row editing if necessary.
        
        returns the indexes of the columns that have been edited.
        """
        line = self._getrow(row)
        if "X" not in line:
            index = np.where(np.all(np.array([int(c) for c in line]) == self.possible_rows, axis = 1))
            if index[0].shape[0]:
                self.possible_rows = np.delete(self.possible_rows, index, axis = 0)
            return []
        
        solutions = self._get_solutions(line, self.possible_rows)
        if len(solutions) == 0:
            raise ValueError("No solutions found")
        
        changes = []
        if len(solutions) == 1:
            index = np.where(np.all(solutions[0] == self.possible_rows, axis = 1))
            self.possible_rows = np.delete(self.possible_rows, index, axis = 0)
            for match in re.finditer(r"X", line):
                index = match.start()
                self[row, index] = str(solutions[0][index])
                changes.append(index)
            return changes
        
        eq = np.where(np.all(solutions == solutions[0], axis=0))[0]
        for i in eq:
            if line[i] == "X":
                self[row, i] = str(solutions[0][i])
                changes.append(i)
        
        return changes
    
    def _check_column(self, column: int) -> list[int]:
        """Compare possible options for given column editing if necessary.
        
        returns the indexes of the rows that have been edited.
        """
        line = self._getcolumn(column)
        if "X" not in line:
            index = np.where(np.all(np.array([int(c) for c in line]) == self.possible_columns, axis = 1))
            if index[0].shape[0]:
                self.possible_columns = np.delete(self.possible_columns, index, axis = 0)
            return []
        
        solutions = self._get_solutions(line, self.possible_columns)
        if len(solutions) == 0:
            raise ValueError("No solutions found")
        
        changes = []
        if len(solutions) == 1:
            index = np.where(np.all(solutions[0] == self.possible_columns, axis = 1))
            self.possible_columns = np.delete(self.possible_columns, index, axis = 0)
            for match in re.finditer(r"X", line):
                index = match.start()
                self[index, column] = str(solutions[0][index])
                changes.append(index)
            return changes
        
        eq = np.where(np.all(solutions == solutions[0], axis=0))[0]
        for i in eq:
            if line[i] == "X":
                self[i, column] = str(solutions[0][i])
                changes.append(i)
        
        return changes
    
    def _iterate_rows(self, indices: Iterable[int]):
        """Iterate over the rows and check for changes.
        
        This will iterate over the rows and check for changes.
        """
        for i in indices:
            column_changes = self._check_row(i)
            self._iterate_columns(column_changes)
        
    def _iterate_columns(self, indices: Iterable[int]):
        """Iterate over the columns and check for changes.
        
        This will iterate over the columns and check for changes.
        """
        for i in indices:
            row_changes = self._check_column(i)
            self._iterate_rows(row_changes)
    
    def _loop(self):
        """Single loop over the puzzle.
        """
        self._iterate_rows(range(self.size))
        self._iterate_columns(range(self.size))

    def solve(self):
        """Solve the puzzle.
        
        This will solve the puzzle by checking all rows and columns.
        """
        while "X" in self.puzzle:
            self._loop()
        
    def __repr__(self):
        return "\n".join([self.puzzle[i * self.size:(i + 1) * self.size] for i in range(self.size)])

    @staticmethod
    def from_url(url: str):
        """Create a Binairo object from a given url.
        
        This will create a Binairo object from a given url.
        """
        html = requests.get(url).text
        return Binairo.from_html(html)

    @staticmethod
    def from_html(html: str):
        """Create a Binairo object from a given html.
        
        This will create a Binairo object from a given html.
        """
        _, _, html, *_ = html.split('<script type="text/javascript">')
        size = int(re.findall(r"var puzzel = new Array\((\d+)\);", html)[0])
        solution = np.zeros((size, size), dtype = int)
        puzzle = np.zeros((size, size), dtype = int)
        
        for match in re.finditer(r"puzzel\[(\d+)\]\[(\d+)\] = '(0|1|-)';", html):
            i, j, value = match.groups()
            puzzle[int(i), int(j)] = value if value != "-" else 2

        for match in re.finditer(r"oplossing\[(\d+)\]\[(\d+)\] = '(0|1)';", html):
            i, j, value = map(int, match.groups())
            solution[i, j] = value

        puzzle = "".join([str(value) if value != 2 else "X" for value in puzzle.flatten()])
        solution = "".join([str(value) for value in solution.flatten()])

        return Binairo(puzzle), Binairo(solution)

    def __eq__(self, other: Self):
        return self.puzzle == other.puzzle
    
if __name__ == "__main__":
    puzzle = Binairo("puzzle.txt")
    puzzle.solve()
    print(puzzle)