#!/usr/bin/env python3

from logic import *

class ParticipantsStrategy(StrategyTemplate):
    def game_tick(self, game):
        game.set_debug_level(1)
        if self.get_phase().value == PlayerPhase.START.value:
            if game.get_remaining_cards_count() == 1:
                game.work()
                return
            if self.ideal_play(game) is not None:
                if self.min_ideal_val_for_work(self._get_my_cards(),\
                                               game.get_remaining_cards_count())\
                   > self.ideal_play(game)[2]:
                    game.study()
                else:
                    game.work()
            else:
                game.work()
        elif self.get_phase().value == PlayerPhase.PLAYING.value:
            if self.ideal_play(game, True) is None:
                self.discard_cards(game)
        elif self.get_phase().value == PlayerPhase.DISCARDING.value:
            self.discard_cards(game)
        else:
            pass
        return

    def count_effectivity(self, problem, cards, game):
        #print("count_effectivity")
        # sum params
        techniques = {}
        for card in cards:
            for t in card.techniques:
                if t in techniques:
                    techniques[t] += card.techniques[t]
                else:
                    techniques[t] = card.techniques[t]
        
        #print(techniques)
        conditions = {}
        conditions_count = 0
        for card in cards:
            for c in card.conditions:
                if c in conditions:
                    conditions[c] = max(card.conditions[c], conditions[c])
                else:
                    conditions[c] = card.conditions[c]
                conditions_count += 1
        for c in conditions:
            if c in techniques:
                if conditions[c] <= techniques[c]:
                    pass
                else:
                    #print("return -1")
                    return -1
            else:
                #print("return -1")
                return -1

        # count power solution
        power = 0
        for t in problem.techniques:
            if t in techniques:
                power += techniques[t] * problem.techniques[t]
        if problem.best_solution is not None:
            if power <= problem.best_solution:
                #print("return -1")
                return -1
        else:
            if power < problem.difficulty:
                #print("return -1")
                return -1
        # count number of effects
        effects = 0
        for t in problem.techniques:
            if t in techniques:
                effects += techniques[t]
        effectivity = problem.difficulty / effects + 0.1 * conditions_count
        #print("return", effectivity)
        return effectivity

    def ideal_play(self, game, play=False):
        #print("ideal play")
        results = []
        for problem in game.get_active_problems():
            # generate all cards subsets
            for i in range(pow(2, len(self._get_my_cards()))):
                k = i
                j = 0
                cards = []
                while k > 0:
                    if k % 2 == 1:
                        cards.append(self._get_my_cards()[j])
                    j += 1
                    k //= 2
                res = self.count_effectivity(problem, cards, game)
                """
                print("problem: ", problem)
                print("cards: ", cards)
                print("res: ", res)
                """
                results.append((problem, cards, res))
        #print("all ideals")
        if len(results) == 0:
            #print("return none")
            return None
        # get ideal combination
        ideal = results[0]
        for item in results:
            if ideal[2] < item[2]:
                ideal = item
        if ideal[2] == -1:
            #print("return none")
            return None
        if play:
            #print("play:", ideal[0], ideal[1])
            if self.get_phase().value == PlayerPhase.DISCARDING.value:
                print("error")
                game.set_debug_level(3)
            game.solve_problem(ideal[0], ideal[1])
        #print("returning not none from ideal play:", ideal)
        return ideal

    def min_ideal_val_for_work(self, cards, cards_in_queue_count):
        if len(cards) == 4:
            return 0
        elif len(cards) == 3:
            return 0
        elif len(cards) == 2:
            return 0.3
        elif len(cards) == 1:
            return 0.5
    def discard_cards(self, game):
        game.discard_cards(self._get_my_cards()[4:])
        game.end_turn()
