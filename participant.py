#!/usr/bin/env python3

from logic import *

class ParticipantsStrategy(StrategyTemplate):
    def game_tick(self, game):
        game.set_debug_level(1)
        pass