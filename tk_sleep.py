import tkinter as tk

def tk_sleep(window, t):
    ms = int(t*1000)
    var = tk.IntVar(window)
    window.after(ms, lambda: 
        var.set(1))
    window.wait_variable(var)