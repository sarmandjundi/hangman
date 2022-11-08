from operator import length_hint
from random import randint
import tkinter as tk
from tkinter import simpledialog, PhotoImage, Frame
from tkinter.ttk import Label
from network import connect, send
from tk_sleep import tk_sleep
from window_handler import create_window, start_window_loop
from style import set_style
from typing import Counter 

game_area_width = 1200
game_area_height = 1000

# TKInter widgets
window = create_window(tk, 'Hangman', game_area_height + 160, game_area_width + 100)
set_style(window)
game_area  = Frame(window, bg='black', bd = 0,\
 height = game_area_height, width = game_area_width)
game_area.place(x=50, y=50)

#ball_image = PhotoImage(file = 'images/ball.png')
#paddle_image = PhotoImage(file = 'images/paddle.png')
#ball = Label(game_area, image = ball_image)
#paddle_1 = Label(game_area, image = paddle_image)
#paddle_2 = Label(game_area, image = paddle_image)
message = Label(game_area, style = 'Message.TLabel')
info_1 = Label(window)
info_2 = Label(window)

game_state = {
    'me': None,
    'opponent': None,
    'is_server': None,
    'shared': {
        'player_1': '',
        'player_2': '',
        'guess_left': 0,
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
    # key_downs (only of interest to the server)
    global keys_down_me, keys_down_opponent
    if game_state['is_server']:
        if user == game_state['me'] and type(message) is list:
            keys_down_me = set(message)
        if user == game_state['opponent'] and type(message) is list:
            keys_down_opponent = set(message)
    # shared state (only of interest to the none-server)
    if type(message) is dict and not game_state['is_server']:
        game_state['shared'] = message
        redraw_screen()
        
        
def redraw_screen():
    player_1, player_2, lives_1, lives_2,\
    score_1, score_2, game_over_message =\
        game_state['shared'].values()
''' info_1.config(text = (
       f'\nPlayer: {player_1}\n' +
       f'Score: {score_1}\n' +
       f'Lives: {lives_1}'
    ))
    info_2.config(text = (
       f'\nPlayer: {player_2[0:10]}\n' +
       f'Score: {score_2}\n' +
       f'Lives: {lives_2}'
    ))
    info_1.place(x = 50, y = game_area_height + 50)
    info_2.place(x = game_area_width - 100, y = game_area_height + 50)
    if game_over_message != '':
        message = Label(game_area, style = 'Message.TLabel')
        message.config(text = game_over_message)
        message.place(y = 200, x = 100, width = game_area_width - 200)     ''' 

def game_loop():
    # unpack game_state['shared'] to variables
    shared = game_state['shared']
    # who is player 1 (= me) and 2 (= opponent)
    shared['player_1'] = game_state['me']
    shared['player_2'] = game_state['opponent']
    guess = ''
    completed_word = 0
    empty_word = ''
    used_letters = ''
    guess_count = 0 
    guess_limit = 5
    out_of_guesses = False
    words = ['football']
    length = len(words)
    for letter in words[0]:
        letter = "_ "
        empty_word += letter

    empty_word = empty_word.split()

    secretword = words[0]
    letters_used = ''
    while True:
        message = Label(game_area, style = 'Message.TLabel')
        message.config(text = ' '.join(empty_word))
        message.place(y = 800, x = 100, width = game_area_width - 200)
        
        if guess_count < guess_limit:
            guess = simpledialog.askstring('Guess', 'Enter guess', parent=window)
            if len(guess) > len(words[0]):
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
            break
        if completed_word == len(secretword):
            break
        if out_of_guesses:
            break    
        
        tk_sleep(window, 1 / 24)

        # send state
        send(game_state['shared'])
        # redraw screen
        redraw_screen()
        # the game is over if there is a game over message
        if shared['game_over_message'] != '':
            break    
    if out_of_guesses:
        message = Label(game_area, style = 'Message.TLabel')
        message.config(text = 'Out of guesses, YOU LOSE!')
        message.place(y = 400, x = 100, width = game_area_width - 200)
        message = Label(game_area, style = 'Message.TLabel')
        message.config(text = ' '.join(empty_word))
        message.place(y = 800, x = 100, width = game_area_width - 200)
    else:
        message = Label(game_area, style = 'Message.TLabel')
        message.config(text = 'YOU WIN! the word was: ' + secretword)
        message.place(y = 400, x = 100, width = game_area_width - 200) 
        message = Label(game_area, style = 'Message.TLabel')
        message.config(text = ' '.join(empty_word))
        message.place(y = 800, x = 100, width = game_area_width - 200)       

# start - before game loop
def start():
    # hide some things initially
    ### j('.wait, .ball, .paddle-1, .paddle-2').hide()
    # show the content/body (hidden by css)
    ### j('body').show()
    # connect to network
    game_state['me'] = simpledialog.askstring(
        'Input', 'Your user name', parent=window)
    # note: adding prefix so I don't disturb
    # other class mates / developers using the same
    # network library
    channel = 'sarmand_hangman_' + simpledialog.askstring(
        'Input', 'Channel', parent=window)
    connect(channel=channel, user=game_state['me'], handler=on_network_message)
    message.config(text = 'Waiting for an opponent...')
    message.place(y = 200, x = 100, width = game_area_width - 200)
    # wait for an opponent 
    while game_state['opponent'] == None:
        print('waiting')
        #tk_sleep(window, 1 / 10)
    message.destroy()
    # start game loop if i am the server
    if not game_state['is_server']:
        game_loop()

# start
start()
start_window_loop(window)

    
    
 