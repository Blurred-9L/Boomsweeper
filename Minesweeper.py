import random
import itertools
import functools

class MinesweeperError(Exception):
  pass

class MineBox:

  def __init__(self):
    self.is_bomb = False
    self.is_visible = False
    self.flagged = False
    self.n_adj_mines = 0
    
  def __str__(self):
    return self.to_str(True)
    
  def to_str(self, debug=False):
    if self.flagged:
      out_str = ' * '
    elif not self.is_visible and not debug:
      out_str = ' . '
    elif self.is_bomb:
      out_str = ' X '
    elif self.n_adj_mines > 0:
      out_str = ' ' + str(self.n_adj_mines) + ' '
    else:
      out_str = ' o '
      
    return out_str

class MineField:
  
  def __init__(self, n_rows, n_cols, n_mines):
    # initialize all fields
    self.rows = n_rows
    self.cols = n_cols
    self.n_mines = n_mines
    self.field = []
    
    # generate the mine field grid
    for i in range(n_rows):
      self.field.append([])
      for j in range(n_cols):
        self.field[i].append(MineBox())
        
    # place the mines into the field
    self.reset()
      
  def __str__(self):
    return self.to_str(True)
    
  def to_str(self, debug=False):
    out_str = ''
    for i in range(self.rows):
      for j in range(self.cols):
        out_str += self.field[i][j].to_str(debug)
      out_str += "\n"
    return out_str
  
  def reset(self):
    n_mines = 0
    while n_mines < self.n_mines:
      # NOTE: randint generate a number in range [0, N]
      row = random.randint(0, self.rows - 1)
      col = random.randint(0, self.cols - 1)
      if not self.field[row][col].is_bomb:
        self.field[row][col].is_bomb = True
        n_mines += 1
        
    self.compute_neighbors()
    
  def compute_neighbors(self):
    for i in range(self.rows):
      for j in range(self.cols):
        # compute all neighboring positions (x, y)
        neighbors = self.find_neighbors(i, j)
                
        # sum all neighboring mines
        self.field[i][j].n_adj_mines = (
          functools.reduce(
            lambda x, y: 
            x + (1 if self.field[y[0]][y[1]].is_bomb else 0),
            neighbors, 
            0
          )
        )
        
  def find_neighbors(self, row, col):
    # compute all neighbors and then filter the invalid positions
    neighbors = list(filter(
                  lambda x: (self.valid_position(x[0], x[1])),
                  itertools.product(
                    range(row - 1, row + 2), 
                    range(col - 1, col + 2)
                  )
                ))
                
    return neighbors
        
  def valid_position(self, row, col):
    return (row >= 0 and row < self.rows and col >= 0 and col < self.cols)
        
  def open(self, row, col):
    self.field[row][col].is_visible = True
    self.field[row][col].flagged = False
    
    if (not self.field[row][col].is_bomb and 
        self.field[row][col].n_adj_mines == 0):
      self.open_neighbors(row, col)
    
  def open_neighbors(self, row, col):
    neighbors = self.find_neighbors(row, col)
    pending = list(filter(
                lambda x: (not self.field[x[0]][x[1]].is_visible and
                           not self.field[x[0]][x[1]].is_bomb and
                           not self.field[x[0]][x[1]].flagged),
                neighbors
              ))
    
    for pos in pending:
      self.field[pos[0]][pos[1]].is_visible = True
      if self.field[pos[0]][pos[1]].n_adj_mines == 0:
        self.open_neighbors(pos[0], pos[1])
        
  def flag(self, row, col):
    self.field[row][col].flagged = not self.field[row][col].flagged
        
  def check_completed(self):
    # TODO: I think we also want to check all non-bombs are open
    target = self.n_mines
    for i in range(self.rows):
      for j in range(self.cols):
        if self.field[i][j].is_bomb and self.field[i][j].flagged:
          target -= 1
          
    return (target == 0)
    
        
class Minesweeper:
  # Constants for difficulty levels
  MS_EASY = 0
  MS_MEDIUM = 1
  MS_HARD = 2

  # Valid commands for the execute() method
  VALID_COMMANDS = ['pick', 'reset', 'flag', 'level', 'quit']
  
  # Valid strings and their constant mapping for each level
  VALID_LEVELS = {'easy' : MS_EASY, 'medium' : MS_MEDIUM, 'hard' : MS_HARD}
    
  # Number or rows, columns and mines per difficulty level
  MS_GRID_VALS = ((10, 10, 10), (16, 16, 40), (16, 30, 50))
  
  # Constants for return values of the execute() method
  MS_RESPONSE_CONTINUE = 0
  MS_RESPONSE_QUIT = 1
  MS_RESPONSE_LOSE = 2
  MS_RESPONSE_WON = 3

  def __init__(self, level=MS_EASY):
    random.seed()
    self.level = level
    level_args = Minesweeper.MS_GRID_VALS[level]
    self.game = MineField(level_args[0], level_args[1], level_args[2])
    
  def execute(self, args):
    # Validate the command argument list
    if len(args) == 0:
      raise Exception("No command given!")  
  
    # It must be a known command
    cmd = args[0]
    if cmd not in Minesweeper.VALID_COMMANDS:
      raise MinesweeperError("Invalid command: " + cmd + "!")
      
    if cmd == "quit":
      return Minesweeper.MS_RESPONSE_QUIT
    elif cmd == "pick" or cmd == "flag":
      # Validate the number of arguments for these commands:
      # <cmd> <row> <column>
      if len(args) != 3:
        raise MinesweeperError("Invalid number of arguments for '" + cmd + 
                               "' command!")

      # Must be an indexable position
      (row, col) = (int(args[1]), int(args[2]))
      if not self.game.valid_position(row, col):
        raise MinesweeperError("Specified position is invalid!")

      # It is an error to pick the same cell twice or to flag an open cell
      if self.game.field[row][col].is_visible:
        raise MinesweeperError("Specified cell is already open!")

      if cmd == "pick":
        # Peek into the mine box
        # This recursively opens any empty cells
        self.game.open(row, col)
        
        # Signal "game lost" if picked a bomb
        if self.game.field[row][col].is_bomb:
          return Minesweeper.MS_RESPONSE_LOSE
      else:
        # Toggle the cell
        self.game.flag(row, col)
        
        # Check if user has won...
        if self.game.check_completed():
          return Minesweeper.MS_RESPONSE_WON
    elif cmd == 'level':
      # Validate the number of arguments
      # level <level-val>
      if len(args) != 2:
        raise MinesweeperError("Invalid number of arguments for '" + cmd +
                               "' command!")
      
      # It must be a known level name
      level = args[1]
      if level not in Minesweeper.VALID_LEVELS.keys():
        raise MinesweeperError("Specified level is invalid!")
        
      self.level = Minesweeper.VALID_LEVELS[level]
      level_args = Minesweeper.MS_GRID_VALS[self.level]
      self.game = MineField(level_args[0], level_args[1], level_args[2])
      self.game.reset()
    else:
      level_args = Minesweeper.MS_GRID_VALS[self.level]
      self.game = MineField(level_args[0], level_args[1], level_args[2])
      self.game.reset()
      
    # continue the game
    return Minesweeper.MS_RESPONSE_CONTINUE