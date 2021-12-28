import tkinter as tk
from tkinter import ttk

from Minesweeper import Minesweeper
from Minesweeper import MinesweeperError

class MinesweeperGUI(ttk.Frame):
  
  def __init__(self, master=None):
    ttk.Frame.__init__(self, master)
    self.gamectx = Minesweeper()
    self.status = Minesweeper.MS_RESPONSE_CONTINUE
    
    # Initialize the underlying app
    self.grid()
    self.add_widgets()
    
  def add_widgets(self):
    # The options frame contains the RESET and the QUIT buttons
    self.options_frame = ttk.Frame(self);
    self.options_frame.grid(row=0, column=0)
    
    self.reset_button = tk.Button(
      self.options_frame, 
      text='Reset',
      command=self.reset_handler
    )
    self.reset_button.grid(row=0, column=0)
    
    self.quit_button = tk.Button(self.options_frame, text='Quit', 
                                 command=self.quit)
    self.quit_button.grid(row=0, column=1)
    
    # The buttons frame contains the Minesweeper buttons
    self.buttons_frame = ttk.Frame(self);
    self.buttons_frame.grid(row=1, column=0)
    
    self.buttontexts = []
    self.buttons = []
    for i in range(self.gamectx.game.rows):
      self.buttontexts.append([])
      self.buttons.append([])
      
      for j in range(self.gamectx.game.cols):
        def dispatcher(event, self=self, row=i, col=j):
          return self.button_handler(event, row, col)
          
        button_str = tk.StringVar()
        button = tk.Button(
          self.buttons_frame, 
          textvariable=button_str
        )
        
        self.buttontexts[i].append(button_str)
        self.buttons[i].append(button)
        self.buttons[i][j].grid(row=i, column=j)
        
        self.buttontexts[i][j].set(self.gamectx.game.field[i][j].to_str())
          
        # Bind the events to our dispatcher function...
        # NOTE: Unfortunately, binding like this makes it so that even when
        # we set the button's status to DISABLED, events are still fired.
        # This is handled in the button_handler callback.
        self.buttons[i][j].bind('<Button-1>', dispatcher)
        self.buttons[i][j].bind('<Button-2>', dispatcher)
        self.buttons[i][j].bind('<Button-3>', dispatcher)
        
  def reset_to_easy(self):
    self.reset_to_level('easy')
    
  def reset_to_medium(self):
    self.reset_to_level('medium')
    
  def reset_to_hard(self):
    self.reset_to_level('hard')
    
  def reset_to_level(self, level):
    args = ['level', level]
    self.gamectx.execute(args)
    self.status = Minesweeper.MS_RESPONSE_CONTINUE
    
    for elem in self.grid_slaves():
      elem.destroy()
      
    self.add_widgets()
       
  def reset_handler(self):
    args = ['reset']
    self.gamectx.execute(args)
    self.status = Minesweeper.MS_RESPONSE_CONTINUE
    self.update_buttons()
        
  def button_handler(self, event, row, col):
    if self.status != Minesweeper.MS_RESPONSE_CONTINUE:
      return
      
    args = [None, row, col]    
    args[0] = 'pick' if event.num == 1 else 'flag'
    try:
      self.status = self.gamectx.execute(args)
    except MinesweeperError as e:
      self.status = Minesweeper.MS_RESPONSE_CONTINUE
    self.update_buttons()
    
  def update_buttons(self):
    show_all = (self.status == Minesweeper.MS_RESPONSE_LOSE or
                self.status == Minesweeper.MS_RESPONSE_WON)
    
    # This is terrible! Updates the text on all the buttons!
    for i in range(self.gamectx.game.rows):
      for j in range(self.gamectx.game.cols):
        self.buttontexts[i][j].set(
          self.gamectx.game.field[i][j].to_str(show_all)
        )
        
        if (self.gamectx.game.field[i][j].is_visible or show_all):
          self.buttons[i][j].config(state=tk.DISABLED, relief=tk.SUNKEN)
        else:
          self.buttons[i][j].config(state=tk.NORMAL, relief=tk.RAISED)
    
root = tk.Tk()
gui = MinesweeperGUI(root)
gui.master.title('Minesweeper')

menubar = tk.Menu(root)
root.config(menu=menubar)

gamemenu = tk.Menu(menubar, tearoff=0)
gamemenu.add_command(label='Easy', command=gui.reset_to_easy)
gamemenu.add_command(label='Medium', command=gui.reset_to_medium)
gamemenu.add_command(label='Hard', command=gui.reset_to_hard)
menubar.add_cascade(label='Level', menu=gamemenu)

gui.mainloop()