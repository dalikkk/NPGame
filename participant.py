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
                print("Ideal play is none")
                if len(self._get_my_cards()) >= 3:
                    game.work()
                else:
                    game.study()
        elif self.get_phase().value == PlayerPhase.PLAYING.value:
            if self.ideal_play(game, True) is None:
                self.discard_cards(game)
        elif self.get_phase().value == PlayerPhase.DISCARDING.value:
            self.discard_cards(game)
        else:
            pass
        return

    def count_effectivity(self, problem, cards, game, reduce_from=None,
                          copied_card=None):
        #print("count_effectivity")
        # sum params
        techniques = {}
        meta_technique = False
        reduction = False
        self_reference = False
        for card in cards:
            for t in card.techniques:
                if t in techniques:
                    techniques[t] += card.techniques[t]
                else:
                    techniques[t] = card.techniques[t]
                if card.name == "Meta-technika":
                    meta_technique = True
                elif card.name == "Redukce":
                    reduction = True
                elif card.name == "Sebe-reference":
                    self_reference = True
        
        conditions = {}
        conditions_count = 0
        for card in cards:
            for c in card.conditions:
                if c in conditions:
                    conditions[c] = max(card.conditions[c], conditions[c])
                else:
                    conditions[c] = card.conditions[c]
            conditions_count += 1
        my_cards = list(cards)
        for card in cards:
            my_cards.remove(card)
            if not card_condition_fulfilled(card, my_cards):
                return -1
            my_cards.append(card)

        # count power solution
        power = 0
        for t in problem.techniques:
            if t in techniques:
                power += techniques[t] * problem.techniques[t]
        if not are_cards_enough_to_solve(problem, cards):
            return -1
        # count number of effects
        effects = 0
        for t in problem.techniques:
            if t in techniques:
                effects += techniques[t]
        if meta_technique:
            effects += 2
        if self_reference:
            effects -= 1
        if reduction:
            effects += 3
        effectivity = problem.difficulty / effects + 0.1 * conditions_count
        return effectivity

    def ideal_play(self, game, play=False):
        results = []
        for problem in game.get_active_problems():
            # generate all cards subsets
            for i in range(pow(2, len(self._get_my_cards()))):
                k = i
                j = 0
                cards = []
                reduction_index = -1
                meta_technics_index = -1
                while k > 0:
                    if k % 2 == 1:
                        cards.append(self._get_my_cards()[j])
                        if cards[-1].name == "Redukce":
                            reduction_index = j
                        if cards[-1].name == "Meta-technika":
                            meta_technics_index = j
                    j += 1
                    k //= 2
                problem_to_reduce = None
                card_imitation = None
                if reduction_index != -1:
                    best_power = -1
                    for p in game.get_active_problems():
                        power = calculate_power_of_solution\
                                (problem, cards, reduce_from = p)
                        if power > best_power:
                            problem_to_reduce = p
                res = -1
                if meta_technics_index != -1:
                    best_res = -1
                    for card in cards:
                        if card.name == "Meta-technika":
                            continue
                        print("count_effectivity", problem, cards, game,
                              problem_to_reduce, card)
                        res = self.count_effectivity\
                              (problem, cards, game=game,
                               reduce_from=problem_to_reduce,
                               copied_card=card)
                        print("effectivity counted")
                        if res > best_res:
                            best_res = res
                            card_imitation = card
                    res = best_res
                else:
                    print("count_effectivity", problem, cards, game,
                          problem_to_reduce)
                    res = self.count_effectivity(problem, cards, game,
                                                 reduce_from=problem_to_reduce)
                    print("effectivity counted")
                """
                print("problem: ", problem)
                print("cards: ", cards)
                print("res: ", res)
                """
                results.append((problem, cards, res, card_imitation,
                                problem_to_reduce))
        if len(results) == 0:
            return None
        # get ideal combination
        ideal = results[0]
        for item in results:
            if ideal[2] < item[2]:
                ideal = item
        if ideal[2] == -1:
            return None
        if play:
            if self.get_phase().value == PlayerPhase.DISCARDING.value:
                print("error")
                game.set_debug_level(3)
            game.solve_problem(ideal[0], ideal[1], copied_card=ideal[3],
                               reduce_from=problem_to_reduce)
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
