#!/usr/bin/env python3

"""
Author: Hugo Adamove
Modifications (minor): Ondra Borysek

"""

from tkinter import *

dont_open_any_other_windows = False

class GameGUI:
    def __init__(self, master, game_stages):
        self.master = master
        self.game_stages = game_stages
        self.current_stage = -1

        master.title("NP hra")
        master.resizable(False, False)

        self.canvas = Canvas(master, width=1024, height=600, bg="#282828")
        self.canvas.grid(row=0, column=0)
        self.create_elements()
        self.next_stage()


    def create_elements(self):
        self.my_cards = [None for i in range(6)]
        self.my_cards_text = [None for i in range(6)]
        self.opponent_cards = [None for i in range(6)]
        x0 = 247
        for i in range(6):
            self.my_cards[i] = self.canvas.create_rectangle(x0, 470, x0+80, 590, fill="lightgreen")
            self.my_cards_text[i] = self.canvas.create_text((x0+40, 474), text="Card name", anchor="n", width=72, justify="c")
            self.opponent_cards[i] = self.canvas.create_rectangle(x0, 10, x0+80, 130, fill="#e3e3e3")
            x0 += 90


        self.problems = [None for i in range(9)]
        self.problems_text = [None for i in range(9)]
        x0 = 112
        for i in range(8):
            self.problems[i] = self.canvas.create_rectangle(x0, 240, x0+80, 360, fill="lightblue")
            self.problems_text[i] = self.canvas.create_text((x0+40, 244), text="Card name", anchor="n", width=72, justify="c")
            x0 += 90

        self.draw_pile = self.canvas.create_rectangle(60, 430, 140, 550, fill="lightgreen")
        self.draw_pile_text = self.canvas.create_text((100, 460), text="Draw pile\n\nx cards remaining", anchor="n", width=72, justify="c")
        
        self.scoreboard = self.canvas.create_text((10, 10), text="Scores", fill="white", anchor="nw")
        self.action_log = self.canvas.create_text((512, 415), text="You did that and that", anchor="c", fill="white")
        self.full_log = ""

        self.button_next_frame = Button(self.master, text="Next frame", command=self.next_stage, anchor="n")
        self.button_next_frame.configure(width = 10, bg="#0066FF", relief="flat")
        self.button_next_window = self.canvas.create_window(974, 520, anchor="se", window=self.button_next_frame)

        self.button_close = Button(self.master, text="Close this window", command=self.close_window, anchor="n")
        self.button_close.configure(width = 20, bg="#00FF66", relief="flat")
        self.button__close_window = self.canvas.create_window(974, 550, anchor="se", window=self.button_close)

        self.button_end = Button(self.master, text="End visualisation mode", command=self.end_windows, anchor="n")
        self.button_end.configure(width = 20, bg="#FF6666", relief="flat")
        self.button__end_window = self.canvas.create_window(974, 580, anchor="se", window=self.button_end)


    def next_stage(self):
        self.current_stage += 1
        if len(self.game_stages) > self.current_stage:
            self.update_elements(self.game_stages[self.current_stage])

    def close_window(self):
        print("[ ] Koniec animacie! (okna)")
        #print("Full log:"+self.full_log)
        #self.master.quit()
        self.master.destroy()

    def end_windows(self):
        print("[ ] Koniec her! (vsech her)")
        global dont_open_any_other_windows
        dont_open_any_other_windows = True
        self.close_window()

    def update_elements(self, _game_stage):
        _my_cards, _opponent_card_count, _problems, _remaining_cards, _scores, _action_string = _game_stage
        self.update_my_cards(_my_cards)
        self.update_opponent_cards(_opponent_card_count)
        self.update_problems(_problems)
        self.update_draw_pile(_remaining_cards)
        self.update_scoreboard(_scores)
        self.update_log(_action_string)
        self.full_log += "\n"+_action_string


    def update_my_cards(self, _cards):
        if len(_cards) > 6:
            print('Pokial viem, kariet v ruke by si nemal nikdy mat naraz viac ako 6, asi si nieco zvoral.')
        for i in range(6):
            if len(_cards) <= i:
                self.canvas.itemconfig(self.my_cards[i], state="hidden")
                self.canvas.itemconfig(self.my_cards_text[i], state="hidden")
            else:
                self.canvas.itemconfig(self.my_cards[i], state="normal")
                text = _cards[i].name+"\n\n"+"\n".join([tech[:5]+" "+str(round(float(value),1)) for tech, value in _cards[i].techniques.items()]) #TO-DO
                self.canvas.itemconfig(self.my_cards_text[i], state="normal", text=text)


    def update_opponent_cards(self, _opponent_card_count):
        for i in range(6):
            if _opponent_card_count <= i:
                self.canvas.itemconfig(self.opponent_cards[i], state="hidden")
            else:
                self.canvas.itemconfig(self.opponent_cards[i], state="normal")


    def update_problems(self, _problems):
        for i in range(8):
            if _problems[i].opened == False:
                self.canvas.itemconfig(self.problems[i], state="hidden")
                self.canvas.itemconfig(self.problems_text[i], state="hidden")
            else:
                self.canvas.itemconfig(self.problems[i], state="normal")
                text = str("["+str(_problems[i].difficulty)+"] "+_problems[i].name+"\n"+"\n".join([tech[:5]+" "+str(round(float(value),1)) for tech, value in _problems[i].techniques.items()])+("\n\n\n" if _problems[i].name== "Nejkratší cesta" else "\n\n")+("best: "+str(round(float(_problems[i].best_solution), 1)) if _problems[i].best_solution!= None else "unsolved"))
                self.canvas.itemconfig(self.problems_text[i], state="normal", text=text)


    def update_draw_pile(self, _remaining_cards):
        self.canvas.itemconfig(self.draw_pile_text, text="Draw pile\n\n"+str(_remaining_cards)+" cards remaining")


    def update_scoreboard(self, _scores):
        self.canvas.itemconfig(self.scoreboard, text="Scores:\n"+"\n".join(["Strategy "+str(score[0])+": "+str(score[1]) for score in _scores.items()]))


    def update_log(self, _action_string):
        self.canvas.itemconfig(self.action_log, text=_action_string)



def initialize(game_stages):
    if not dont_open_any_other_windows:
        root = Tk()
        my_gui = GameGUI(root, game_stages)
        root.mainloop()
