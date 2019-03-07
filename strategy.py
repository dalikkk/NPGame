#!/usr/bin/env python3

from logic import Player, PlayerPhase, calculate_power_of_solution, are_cards_enough_to_solve, StrategyTemplate


class ProofS(StrategyTemplate):
    def game_tick(self, game):
        self._name = "ProofS"
        game.work()
        game.discard_cards(self._get_my_cards())
        game.end_turn()

class BasicS(StrategyTemplate):
    def game_tick(self, game):
        if self.get_phase().value == PlayerPhase.START.value:
            game.work()
        else:
            if len(self._get_my_cards()) > 4:
                game.discard_cards(self._get_my_cards()[4:])
            else:
                game.end_turn()

