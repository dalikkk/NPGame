#!/usr/bin/env python3

import copy
from logic import Game
from loadedCards import Card, Problem
import strategy as karlik # comment this out or make karlik.py and fill it out with Karliks strategies
import participant as p


def example_single_match_ProofS_vs_BasicS():
    game_instance = Game()
    game_instance.add_player("Karlik ProofS", karlik.ProofS())
    game_instance.add_player("Karlik BasicS", karlik.BasicS())
    game_instance.start_game()
    print("Number of active problems:", len(game_instance.get_active_problems()))
    print("Game ended:", game_instance.get_current_scores())


def against_participant(n, karlik_prototype):
    return battle_two_prototypes(p.ParticipantsStrategy(), karlik_prototype, n)[1]


def against_participant_with_print(n, karlik_prototype, print_name):
    answer = against_participant(n, karlik_prototype)
    print("Vyhral proti", print_name, answer, "z", n)
    return answer


def single_match_two_prototypes(prototype_a, prototype_b):
    game_instance = Game()
    #game_instance.set_debug_level()
    game_instance.add_player("prototype_a", prototype_a)
    game_instance.add_player("prototype_b", prototype_b)
    game_instance.start_game()
    return dict(game_instance.get_current_scores())


def battle_two_prototypes(prototype_a, prototype_b, n):
    wins = [0, 0]
    for i in range(n):
        try:
            instance_a = copy.deepcopy(prototype_a)
            instance_b = copy.deepcopy(prototype_b)
            if i%2 == 0:
                instance_a, instance_b = instance_b, instance_a
            #print(instance_a, instance_b)
            answer = single_match_two_prototypes(instance_a, instance_b)
            if answer[0] == answer[1]:
                continue
            winner_i = int(answer[0] < answer[1])
            if i%2:
                winner_i = (winner_i + 1)%2
            wins[winner_i] += 1
        except Exception  as e:
            print("Caught exception. Something in the game failed, possibly your solution:", e)
    return wins


if __name__ == "__main__":
    print("[~] Informacni testy")
    against_participant_with_print(5, karlik.ProofS(), "ProofS")
    against_participant_with_print(5, karlik.BasicS(), "BasicS")
    print("[~] Skutecne testy")
    real_answer = against_participant_with_print(80, karlik.ReasonableStrategy(), "ReasonableStrategy")

