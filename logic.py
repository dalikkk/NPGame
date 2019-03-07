#!/usr/bin/env python3

from enum import Enum
from collections import deque
from random import shuffle, randint
from loadedCards import Card, Problem, load_problems, load_techniques
from time import sleep
import random

class GamePhase(Enum):
    INIT = 1
    RUNNING = 2
    RESULTING = 3
    ENDED = 4


class PlayerPhase(Enum):
    START = 1  # muzes Studovat ci Pracovat
    PLAYING = 2  # muzes Resit problemy, Zahodit karty nebo Ukoncit tah
    DISCARDING = 3  # muzes Zahodit karty nebo Ukoncit tah
    ENDED = 4  # Ukoncil tah v aktualnim kole


class Game:
    def __init__(self):
        self._debug_level = 0
        self.__player_count = 0
        self.__players = {}
        self.__game_mode = GamePhase.INIT
        self.__player_order = deque()
        self.__deck = list(load_techniques())
        self.force_deck_shuffle()
        self.__played_cards = []
        self.__action_history = []  # history of successful actions
        self.__problems_active = 1
        self.__problems = list(load_problems())
        self.__force_problems_shuffle()
        self.__problems[0].opened = True
        self.__current_scores = {}
        self.__current_player_id = None
        #print(self.__deck[0].name)

    def force_deck_shuffle(self):
        shuffle(self.__deck)
        #self.__deck = random.sample(self.__deck, len(self.__deck))

    def __force_problems_shuffle(self):
        shuffle(self.__problems)
        #self.__problems = random.sample(self.__problems, len(self.__problems))


    def set_debug_level(self, debug_level = 0):
        self._debug_level = debug_level # 0 means print nothing, 1 is print errors, 2 is print also warnings, 3 is print also information

    def log_msg(self, importance, msg):
        if importance <= self._debug_level:
            print(msg, "| Current player_id:", self.get_current_player().get_id())

    def add_player(self, name, player_type=None):
        new_player = player_type
        if new_player is None:
            new_player = Player()
        new_player._name = name
        new_player._id = self.__player_count
        self.__players[new_player.get_id()] = new_player
        self.__player_count += 1
        self.__player_order.append(new_player.get_id())

    def get_current_player(self):
        return self.__players[self.__current_player_id]

    def _log_action(self, action_type, additional_info=None):
        player_id = self.get_current_player().get_id()
        self.__action_history.append((player_id, action_type, additional_info))
        msg_to_log = "Succesfull action - Player_id: " + str(player_id) + "; Action type: " + str(action_type)
        if additional_info is not None:
            msg_to_log += "; with aditional info: " + str(additional_info)
        self.log_msg(3, msg_to_log)

    def get_player_count(self):
        return self.__player_count

    def get_remaining_cards_count(self):
        return len(self.__deck)

    def get_player_order(self):
        return list(self.__player_order)

    def get_played_cards(self):
        return self.__played_cards[:]

    def get_active_problem_count(self):
        return self.__problems_active

    def get_problems(self):
        return self.__problems[:]

    def get_active_problems(self):
        return list(filter(lambda x: x.opened, self.get_problems()))

    def get_current_scores(self):
        self._total_up_the_game()
        return self.__current_scores

    def get_action_history(self):
        return self.__action_history
    
    def get_players(self):
        return self.__players[:]

    def get_all_techniques(self):
        return list(load_techniques())

    def __add_card_to_player(self, player_id, card=None):
        if player_id not in self.__players:
            return None 
        if card is None and len(self.__deck):
            card = self.__deck.pop()
        if card is not None:
            self.__players[player_id]._cards.append(card) # todo: check if its working

    def start_game(self):
        for _ in range(4):
            for x in self.__players:
                self.__add_card_to_player(x)
        self.__game_mode = GamePhase.RUNNING
        while self.__game_mode.value != GamePhase.ENDED.value:
            self._game_round()
        self.log_msg(3, "[ ] Game successfully finished\n")

    def _solve_problem(self, player_id, problem, cards, additional_info=None):
        cards = cards[:]
        if not problem.opened:
            self.log_msg(1, "[x] Problem you are trying to solve is not opened")
            return None
        if not are_cards_enough_to_solve(problem, cards, additional_info):
            self.log_msg(1, "[x] This cards are not enough to solve the problem")
            return None
        power_of_solution = calculate_power_of_solution(problem, cards, (self, player_id, additional_info)) # this additional info is currently only used for card Redukce

        current_player = self.get_current_player()
        try:
            for single_card in cards:
                if single_card.name == "Sebe-reference":
                    #print("--------------exception--------------", single_card.name)
                    continue
                current_player._cards.remove(single_card)
        except Exception as _:
            self.log_msg(1, "[x] Discarding after Solving problem failed. As a punishment, all your cards are beiing discarded.")
            current_player._cards = []
            return None

        if problem.best_solution is None:
            number_of_unopened_problems = len(self.get_problems()) - len(self.get_active_problems())
            if number_of_unopened_problems > 0:
                self.__problems_active += 1
                open_problem_number = randint(0, number_of_unopened_problems - 1)
                for x in self.get_problems():
                    if x.opened:
                        continue
                    if open_problem_number == 0:
                        self.log_msg(3, "[ ] Opening new problem with name: " + x.name)
                        x.opened = True
                        break
                    open_problem_number -= 1

        problem.best_solution = power_of_solution
        problem.solved_by[player_id] = problem.solved_by.get(player_id, 0) + 1
        self.__played_cards = self.__played_cards + cards

        return True

    def _game_round(self):
        self.log_msg(3, "[ ] Starting new round in game mode: " + str(self.__game_mode))

        if self.__game_mode.value == GamePhase.INIT.value:
            self.__game_mode = GamePhase.RUNNING

        if self.__game_mode.value == GamePhase.RUNNING.value:
            for player_id in self.get_player_order():
                self.__current_player_id = player_id
                #print("\n\tAnother player starts (deck size: ", len(self.__deck), ")")
                if not len(self.__deck):
                    self.__game_mode = GamePhase.RESULTING
                    break
                current_player = self.__players[player_id]
                current_player._phase = PlayerPhase.START
                ticks_count = 0
                while current_player._phase.value != PlayerPhase.ENDED.value:
                    if ticks_count > 100:
                        self.log_msg(1, "[x] Probably cycling - forcing end of turn for player with id: " + str(self.get_current_player().get_id()))
                        # Technicaly i should discard players cards, so he can't keep stacking them up. 
                        # It is disallowed by the rules, but for codes simplicity sake let's keep it this way. 
                        break
                    current_player.game_tick(self)
                    self._total_up_the_game()
                    ticks_count += 1
            self.__player_order.rotate(1)

        if self.__game_mode.value == GamePhase.RESULTING.value:
            self._total_up_the_game()
            self.__game_mode = GamePhase.ENDED

    def _total_up_the_game(self):
        for current_player_id in self.__players:
            current_player_score = 0
            for y in self.__problems:
                current_player_score += y.solved_by.get(current_player_id, 0) * y.difficulty
            self.__current_scores[current_player_id] = current_player_score

# BEGIN --- ACTIONS
    def study(self):
        current_player = self.get_current_player()
        if current_player._phase.value != PlayerPhase.START.value:
            self.log_msg(1, "[x] You are trying to Study after the start of turn. Currently in phase: " + str(current_player.get_phase()))
            return False
        if len(self.__deck) < 2:
            self.log_msg(1, "[x] You can't Study, because there aren't two cards in the deck.")
            return False
        for _ in range(2):
            self.__add_card_to_player(current_player.get_id())
        current_player._phase = PlayerPhase.DISCARDING
        self._log_action("Study")
        return True

    def work(self):
        current_player = self.get_current_player()
        if current_player._phase.value != PlayerPhase.START.value:
            self.log_msg(1, "[x] You are trying to Work after the start of turn. Currently in phase: " + str(current_player.get_phase()))
            return False
        self.__add_card_to_player(current_player.get_id())
        current_player._phase = PlayerPhase.PLAYING
        self._log_action("Work")
        return True

    def solve_problem(self, problem_to_solve, cards_to_use, additional_info=None):
        current_player = self.get_current_player()
        if current_player._phase.value != PlayerPhase.PLAYING.value:
            self.log_msg(1, "[x] You are trying to Solve problem while not in Playing phase. Currently in phase: " + str(current_player.get_phase()))
            return False
        answer = self._solve_problem(current_player.get_id(), problem_to_solve, cards_to_use, additional_info)
        if answer:
            self._log_action("Solve", (problem_to_solve, cards_to_use, additional_info))
        else:
            self.log_msg(1, "[x] Solving poblem failed. Maybe thouse cards aren't enough or the problem isn't opened yet?")
        return answer

    def discard_cards(self, cards_to_discard):
        current_player = self.get_current_player()
        if not (current_player.get_phase().value == PlayerPhase.PLAYING.value or current_player.get_phase().value == PlayerPhase.DISCARDING.value):
            self.log_msg(1, "[x] You are trying to Discards cards while not in Playing or Discarding phase. Currently in phase: " + str(current_player.get_phase()))
            return False
        backup = current_player._cards
        try:
            for single_card in cards_to_discard:
                current_player._cards.remove(single_card)
        except Exception as e:
            self.log_msg(1, "[x] Discarding failed. Are you discarding only cards, that you didn't use yet? Info from exception: " + str(e))
            current_player._cards = backup
            return False
        self.__played_cards = self.__played_cards + cards_to_discard
        self._log_action("Discards", cards_to_discard)
        return True

    def end_turn(self):
        current_player = self.get_current_player()
        if len(current_player._get_my_cards()) > 4:
            self.log_msg(1, "[x] You can't end turn. You have more than 4 cards in hand. Use them to Solve problems or discard some of them.")
            return False
        current_player._phase = PlayerPhase.ENDED
        self._log_action("EndTurn")
        return True

# END --- ACTIONS

# BEGIN --- HELPER FUNCTIONS

def is_problem_reducable_to(reduce_from, reduce_to):
    reduce_from_level = reduce_from.type[:]
    reduce_to_level = reduce_to.type[:]
    levels = {"P":1, "NP":2, "PSCAPE":3, "EXPTIME":4}
    return levels[reduce_from_level] >= levels[reduce_to_level]


def card_condition_fulfilled(card, other_cards):
    if len(card.conditions) == 0:
        return True
    #print("!!!!!", len(card.conditions))
    found = False
    for single_condition in card.conditions:
        if found:
            break
        for o_card in other_cards:
            if o_card.techniques.get(single_condition, False):
                found = True
                break
    return found


def calculate_power_of_solution(problem, cards, additional_info=None):
    current_power = 0
    for single_card in cards:
        other_cards = cards[:]
        other_cards.remove(single_card)
        card_to_add_up = single_card
        if card_condition_fulfilled(card_to_add_up, other_cards):

            if card_to_add_up.name == "Redukce":
                try:
                    (game, player_id, reduce_from) = additional_info.get("redukce", Exception) # todo: add documentation, test get at none
                    if not reduce_from.opened:
                        continue
                    if reduce_from.solved_by.get(player_id, None) is None:
                        continue
                    if not is_problem_reducable_to(reduce_from, problem):
                        continue
                    current_power += problem.best_solution
                except Exception as _:
                    # game.log_msg(2, "[x] You've tried Calculating power of solution with cards including Redukce without suplying aditional information needed to use the card. This way you don't get the benefit from it, but you won't crash because of it.")
                    print("[x] You've tried Calculating power of solution with cards including Redukce without suplying aditional information needed to use the card. This way you don't get the benefit from it, but you won't crash because of it.") # todo: do debug log

            if card_to_add_up.name == "Meta-technika":
                try:
                    copied_card = additional_info # todo: add documentation
                    if copied_card is None:
                        continue
                    if copied_card not in cards:
                        continue
                    card_to_add_up = copied_card
                except Exception as _:
                    game.log_msg(2, "[x] You've tried Calculating power of solution with cards including Meta-technika without suplying aditional information needed to use the card or are copying invalid card. This way you don't get the benefit from it, but you won't crash because of it.")

            for single_technique_key, single_technique_val in card_to_add_up.techniques.items():
                current_power += single_technique_val * problem.techniques.get(single_technique_key, 0)
    return current_power


def are_cards_enough_to_solve(problem, cards, additional_info=None):
    power_of_solution = calculate_power_of_solution(problem, cards, additional_info)
    if problem.best_solution is None:
        return power_of_solution >= problem.difficulty
    else:
        return power_of_solution > problem.best_solution

# END --- HELPER FUNCTIONS


class Player:
    def __init__(self):
        self._id = 1
        self._name = "Karlik"
        self._cards = []
        self._phase = PlayerPhase.START

    def get_id(self):
        return self._id

    def get_name(self):
        return self._name

    def _get_my_cards(self):
        return self._cards

    def get_cards_count(self):
        return len(self._cards)

    def get_phase(self):
        return self._phase

    def game_tick(self, game):
        pass


class StrategyTemplate(Player):
    def game_tick(self, game):
        pass


