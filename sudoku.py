import asyncio


class Sudoku:

    def __init__(self, board):
        self._board = [
            [Square(x, y, self, num=s) for y, s in enumerate(row)]
            for x, row in enumerate(board)
        ]

    def __iter__(self):
        return iter(self._board)

    def __getitem__(self, key):
        return self._board[key]

    async def solve(self):
        """Attempts to solve the board"""

        """TODO:
        Handle guess and checking:
        1) Make guess (Make logical guess based on what could be most impactful...i.e. if two spots can have either number in a row)
        2) Fork based on guess
        3) Check if one raises from impossible square (delete this fork)
        4) Check if one completes (will simply return from .gather)
        5) Each board can recurse through this guess and checking, just in case
        """
        tasks = [square.check() for row in self for square in row]

        return await asyncio.gather(*tasks, return_exceptions=False)

    @classmethod
    def from_cmd_line(cls):
        # Setup an empty board...all None
        square = [x[:] for x in [[None] * 9] * 9]
        finished = ""

        # Loop 1 - 9 for the rows
        for x in range(1, 10):
            # Loop through the columns
            for y in range(1, 10):
                # Set the input to None to prepare for next input
                inp = None
                # Loop while input is None (to ensure given input is correct)
                while inp is None:
                    # Start new line...this'll end up printing an extra newline on first execution, but who cares
                    print("\n")
                    # Print the already filled in spots...just an easy to use string, so we don't loop through again
                    print(finished, end='')
                    # Print the x (current variable we're requesting)
                    print(" x |", end='')
                    # Then print an interpunct for each blank on the rest of the line
                    print(" · |" * (9 - y), end='')
                    # Try to convert to int
                    try:
                        print("\n")
                        # We want to get the input before converting, as we want to also handle blank input
                        inp = input("Fill in the x (leave blank if square is blank): ")
                        inp = int(inp)
                    except ValueError:
                        # If it was a blank input, this is correct...we want to accept this, so make it a space
                        # A space will replace the . and line up in monospace fonts (it's in a cmd line, it should be monospace)
                        inp = " " if inp == "" else None

                # Add to our finished string
                finished = f"{finished} {inp} |"
                # Convert back to None if it was a space, for our actual array
                square[x - 1][y - 1] = inp if inp != " " else None
            # Once a row is done, add a new line to our finished string
            # We don't need to do anything weird with the actual board, since it's logical based on x and y
            finished += "\n"

        # Now that we're done, we can create the Sudoku board and return it
        return cls(square)


class Square:
    """A square inside Sudoku"""

    def __init__(self, row, column, board, num=None):
        self._row = row
        self._column = column
        self._board = board
        self.num = num

    @property
    def row(self):
        return [x.num for x in self._board[self._row]]

    @property
    def column(self):
        return [r[self._column].num for r in self._board]

    @property
    def table(self):
        table_x = int(self._row / 3) * 3
        table_y = int(self._column / 3) * 3
        return [self._board[x][y].num for y in range(table_y, table_y + 3) for x in range(table_x, table_x + 3)]

    @property
    def solved(self):
        # Simple property to check if this square is filled in or not
        return self.num is not None

    def get_possible_numbers(self):
        """Return all possible numbers based on the following criteria:
        1) Restrictions based on what is in the current row
        2) Restrictions based on what is in the current column
        3) Restrictions based on what is in the current table

        TODO: Add more checks that this can handle. (Off the top of my head I'm not sure what else?)
        """

        # Get the differences based on the row/column/table
        possibles = set(range(1, 10)).difference(self.row, self.column, self.table)
        return possibles

    async def check(self):
        """A task that repeatedly checks if this square has a solution. This will raise an error
        if an impossibility is detected"""

        while not self.solved:
            # Get list of possible numbers this square can have
            possibles = self.get_possible_numbers()
            # If there's only once possibility, then use this number...this square is now solved
            if len(possibles) == 1:
                self.num = possibles.pop()
            # If there are no possible squares well...something's wrong, that shouldn't be possible
            # This check is done because we want to be able to guess and check, and figure out if a guess is invalid
            elif len(possibles) == 0:
                raise ValueError("Impossible square; no possible numbers based on restrictions")
            # Otherwise wait a small amount and continue
            else:
                await asyncio.sleep(0.05)


if __name__ == "__main__":
    # TODO: Create GUI?
    s = Sudoku.from_cmd_line()

    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(s.solve())
    for row in s:
        print(" ".join(f"{square.num}" for square in row))
