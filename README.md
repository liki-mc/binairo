# Binairo
Solver for binary puzzles (also called 'binairo' in Dutch).

This repository contains a simple solver for binary puzzles. The rules can be found [here](https://binarypuzzle.com/rules.php). This code was tested on binary puzzles from [binarypuzzle.com](https://binarypuzzle.com/).

As a bonus I also implemented a way to solve the special puzzle of the day, found [here](https://binarypuzzle.com/special.php).

## Usage
The code contains a binary class, that can be called on either a string representing the puzzle, or a file containing this string, an example is found in `binairo.txt`.
```py
from binairo import Binairo
puzzle = Binairo("puzzle.txt")
puzzle.solve()
print(puzzle)
```

Solving puzzles from binarypuzzle.com can be done using `from_url`:
```py
from binairo import Binairo
puzzle, solution = Binairo.from_url("https://binarypuzzle.com/puzzles.php?size=12&level=4&nr=12")
puzzle.solve()
if puzzle == solution:
    print("Successfully solved puzzle")
else:
    print("Made a mistake")
    print(puzzle)
```

There is no step by step solution to this repository. One could override Binairo._check_row and Binairo._check_column to print the steps taken.