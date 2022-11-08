def create_window(tk, title, size_y, size_x):
    # create a new window
    window = tk.Tk()
    # set the title of the window
    window.title(title)
    # get the screen dimensions
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    # calculate window size
    window_width = round(size_x)
    window_height = round(size_y)
    # calculate offset for centering
    center_x = round(screen_width / 2 - window_width / 2)
    center_y = round(screen_height / 2 - window_height / 2)
    # size and offset the window correctly
    window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    return window
 
# Start the main window loop
def start_window_loop(window) :
    try:
        # try to make text less blurry on windows
        # by setting dpi awareness
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except: pass 
    finally:
        # start the main loop of the window
        window.mainloop()