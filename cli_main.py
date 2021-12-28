from Minesweeper import Minesweeper
from Minesweeper import MinesweeperError

def parse_command():
  user_input = input('> ')
  args = user_input.split()
  return args

gamectx = Minesweeper()
status = Minesweeper.MS_RESPONSE_CONTINUE
while status == Minesweeper.MS_RESPONSE_CONTINUE:  
  print(gamectx.game.to_str(False))
  
  try:
    args = parse_command()
    status = gamectx.execute(args)
  except MinesweeperError as e:
    print(str(e))
    
  if status == Minesweeper.MS_RESPONSE_WON:
    print(gamectx.game.to_str(False))
    print("\nGame Won!")
  elif status == Minesweeper.MS_RESPONSE_LOSE:
    print(gamectx.game.to_str(False))
    print("\n" + gamectx.game.to_str(True))
    print("\nGame Over!")