import tkinter as tk
from tkinter import simpledialog, PhotoImage, Frame
from tkinter.ttk import Label
from network import connect, send
from tk_sleep import tk_sleep
from window_handler import create_window
from style import set_style

game_area_width = 1200
game_area_height = 1000

# TKInter widgets
window = create_window(tk, 'Hangman', game_area_height + 160, game_area_width + 100)
set_style(window)
game_area  = Frame(window, bg='black', bd = 0,\
 height = game_area_height, width = game_area_width)
game_area.place(x=50, y=50)

message = Label(game_area, style = 'Message.TLabel')
info_1 = Label(window)
info_2 = Label(window)

game_state = {
    'me': None,
    'opponent': None,
    'is_server': None,
    'shared': {
        'who_is_playing': '',
        'word_to_guess': '',
        'letters_guessed': '',
        'parts_of_word': [],
        'guesses_left': 0,
        'guesses_limit': 0,
        'game_over_message': ''
    }
}

def get_opponent_and_decide_game_runner(user, message):
    # who is the server (= the creator of the channel)
    if 'created the channel' in message:
        name = message.split("'")[1]
        game_state['is_server'] = name == game_state['me']
            
    # who is the opponent (= the one that joined that is not me)
    if 'joined channel' in message:
        name = message.split(' ')[1]
        if name != game_state['me']:
            game_state['opponent'] = name

# handler for network messages
def on_network_message(timestamp, user, message):
    if user == 'system': 
        get_opponent_and_decide_game_runner(user, message)
    # shared state (only of interest to the none-server)
    if type(message) is dict and not game_state['is_server']:
        game_state['shared'] = message
        
        
def game_loop():
    global letters_used, completed_word, used_letters, out_of_guesses,secretword, who_is_playing, completed_word
    guess_limit = game_state['shared']['guesses_limit']
    secretword = game_state['shared']['word_to_guess']   
    completed_word = ''
    used_letters = ''
    guess = ''
    out_of_guesses = False

    while True:
        who_is_playing = game_state['shared']['who_is_playing']    
        while who_is_playing != game_state['me']:
            who_is_playing = game_state['shared']['who_is_playing']
            tk_sleep(window, 1 / 10)        
        guess_count = game_state['shared']['guesses_left']
        empty_word = game_state['shared']['parts_of_word'] 
        guess_limit = game_state['shared']['guesses_limit']
        secretword = game_state['shared']['word_to_guess']   
        letters_used = game_state['shared']['letters_guessed']  
        if((guess_count < 6) and (guess_count > 0)):
            imagename = 'hangman-bilder/' + str(guess_count) +'.png'
            hangman_image = PhotoImage(file = imagename)
            hangman = Label(game_area, image = hangman_image)
            hangman.place(x=100, y=20)
        if letters_used != '': 
            message = Label(game_area, style = 'Message.TLabel')
            message.config(text = 'Letters used: ' + letters_used)
            message.place(y = 700, x = 100, width = game_area_width - 200)  
                   
        message = Label(game_area, style = 'Message.TLabel')
        message.config(text = ' '.join(empty_word))
        message.place(y = 800, x = 100, width = game_area_width - 200)
        
        if guess_count < guess_limit:
            guess = simpledialog.askstring('Guess', 'Enter guess', parent=window)
            if len(guess) > len(secretword):
                message = Label(game_area, style = 'Message.TLabel')
                message.config(text = 'The guess word is longer than the secret word!')
                message.place(y = 400, x = 100, width = game_area_width - 200)
                continue       
        else:
            out_of_guesses = True
        missing_letters = secretword    
        
        for guess_letter in guess:    
            counter = 0
            
            if guess_letter in secretword:
                used_letters += guess_letter
                for letter in secretword:
                    if letter == guess_letter:
                        missing_letters = missing_letters.replace(letter, '')
                        empty_word[counter] = guess_letter
                        if guess_letter in missing_letters:
                            letters_used = letters_used + guess_letter
                            completed_word += 1
                    counter += 1
                    if counter > len(secretword):
                        break               
            else:
                if guess_letter not in letters_used:
                    letters_used = letters_used + guess_letter
                used_letters += guess_letter
                guess_count += 1
                if(guess_count < 6):
                    imagename = 'hangman-bilder/' + str(guess_count) +'.png'
                    hangman_image = PhotoImage(file = imagename)
                    hangman = Label(game_area, image = hangman_image)
                    hangman.place(x=100, y=20)
        message = Label(game_area, style = 'Message.TLabel')
        message.config(text = 'Letters used: ' + letters_used)
        message.place(y = 700, x = 100, width = game_area_width - 200)            
        if '_' not in empty_word:
            game_state['shared']['game_over_message'] = 'YOU WIN! the word was: ' + secretword
        elif completed_word == len(secretword):
            game_state['shared']['game_over_message'] = 'YOU WIN! the word was: ' + secretword
        elif out_of_guesses:
            game_state['shared']['game_over_message'] = 'Out of guesses, YOU LOSE!'   
        message = Label(game_area, style = 'Message.TLabel')
        message.config(text = ' '.join(empty_word))
        message.place(y = 800, x = 100, width = game_area_width - 200)
        game_state['shared']['guesses_left'] = guess_count
        game_state['shared']['parts_of_word'] = empty_word
        game_state['shared']['letters_guessed'] = letters_used
        game_state['shared']['who_is_playing'] = game_state['opponent']
        # send state
        send(game_state['shared'])
        # redraw screen
        # the game is over if there is a game over message
        if game_state['shared']['game_over_message'] != '':
            break    
    message = Label(game_area, style = 'Message.TLabel')
    message.config(text = game_state['shared']['game_over_message'])
    message.place(y = 400, x = 100, width = game_area_width - 200)
    message.config(text = ' '.join(empty_word))
    message.place(y = 800, x = 100, width = game_area_width - 200)       

# start - before game loop
def start():
    global empty_word, secretword, guess_limit, guess_count
    empty_word = ''
    secretword = 'football'
    game_state['me'] = simpledialog.askstring(
        'Input', 'Your user name', parent=window)

    channel = 'sarmand_' + simpledialog.askstring(
        'Input', 'Channel', parent=window)
    connect(channel=channel, user=game_state['me'], handler=on_network_message)
    message.config(text = 'Waiting for an opponent...')
    message.place(y = 200, x = 100, width = game_area_width - 200)
    # wait for an opponent 
    while game_state['opponent'] == None:
        tk_sleep(window, 1 / 10)
    message.destroy()
    if game_state['is_server']:
        for letter in secretword:
            letter = "_ "
            empty_word += letter
        empty_word = empty_word.split()
        guess_limit = 5
        guess_count = 0  
        if game_state['shared']['who_is_playing'] == '':
            game_state['shared']['who_is_playing'] = game_state['me']
            game_state['shared']['word_to_guess'] = secretword
            game_state['shared']['guesses_left'] = guess_count
            game_state['shared']['parts_of_word'] = empty_word
            game_state['shared']['guesses_limit'] = guess_limit
            send(game_state['shared'])
    game_loop()

# start
start()
window.mainloop()
#start_window_loop(window)

    
    
 