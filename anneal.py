import math
import random

class Annealer(object):
    def __init__(self, energy_func, do_move_func, undo_move_func, copy_func, listener):
        self.energy_func = energy_func
        self.do_move_func = do_move_func
        self.undo_move_func = undo_move_func
        self.copy_func = copy_func
        self.listener = listener
    def anneal(self, state, max_temp, min_temp, steps):
        factor = -math.log(float(max_temp) / min_temp)
        energy = self.energy_func(state)
        previous_energy = energy
        best_energy = energy
        best_state = self.copy_func(state)
        if self.listener:
            self.listener(best_state, best_energy)
        for step in xrange(steps):
            temp = max_temp * math.exp(factor * step / steps)
            undo_data = self.do_move_func(state)
            energy = self.energy_func(state)
            change = energy - previous_energy
            if change > 0 and math.exp(-change / temp) < random.random():
                self.undo_move_func(state, undo_data)
            else:
                previous_energy = energy
                if energy < best_energy:
                    best_energy = energy
                    best_state = self.copy_func(state)
                    if self.listener:
                        self.listener(best_state, best_energy)
                    if energy <= 0:
                        break
        return best_state, best_energy
