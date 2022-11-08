import tkinter as tk
from tkinter.ttk import Style
 
# Tkinter will let you define styles for widgets
# in a way semi-similar to how CSS styling works
def set_style(win):
 
    win.configure(
        background = "#515151"
    )
 
    style = Style()
    
    style.theme_use('classic')
    
    style.configure(
        'TLabel', 
        background = '#515151', 
        foreground = '#fff',
        borderwidth = 0,
        font = (
            'TkDefaultFont',
            18
        )
    )

    style.configure(
        'Message.TLabel',
        background = '#000000',
        anchor = tk.CENTER,
        font = (
            'TkDefaultFont',
            24
        )
    )