import numpy as np
import os

from binairo import Binairo

class SpecialBinairo:
    def __init__(self, puzzle: str | os.PathLike | Binairo, subsize: int):
        self.puzzle = Binairo(puzzle)
        self.subsize = subsize

        self.subpuzzles: list[list[Binairo]] = []
        for i in range(0, self.puzzle.size, subsize):
            self.subpuzzles.append([Binairo(self.puzzle[i:i+subsize, j:j+subsize]) for j in range(0, self.puzzle.size, subsize)])
    
    def __repr__(self):
        return f"SpecialBinairo({self.puzzle}, {self.subsize})"

    def _update_puzzle(self):
        """Update the puzzle with the subpuzzles.
        """
        for i, row in enumerate(self.subpuzzles):
            rows = [""] * self.subsize
            for subpuzzle in row:
                puzzle = [subpuzzle[j] for j in range(self.subsize)]
                for j in range(self.subsize):
                    rows[j] += puzzle[j]
            
            for j in range(self.subsize):
                self.puzzle._setrow(i*self.subsize + j, rows[j])
    
    def _update_subpuzzles(self):
        """Update the subpuzzles with the puzzle.
        """
        for i, row in enumerate(self.subpuzzles):
            for j, subpuzzle in enumerate(row):
                subpuzzle.puzzle = self.puzzle[i*self.subsize:(i+1)*self.subsize, j*self.subsize:(j+1)*self.subsize]
    
    def solve(self):
        """Solve the puzzle.
        """
        while "X" in self.puzzle.puzzle:
            for row in self.subpuzzles:
                for subpuzzle in row:
                    subpuzzle._loop()

            self._update_puzzle()

            self.puzzle._loop()
            self._update_subpuzzles()

a = SpecialBinairo("puzzle2.txt", 8)
a.solve()
print(a.puzzle)