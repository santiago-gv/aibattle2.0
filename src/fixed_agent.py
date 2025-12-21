import random

class FixedAgent:

    def __init__(self, character):
        self.is_defending = False
        self.character = character

    def choose_action(self, enemy=None):
        
        if self.character.get_cooldown() <= 0:
            
            #Random entre super attack, attack i defend
            return random.choice(["super_attack", "attack", "defend"])
        else:
            #Random entre attack i defend
            return random.choice(["attack", "defend"])

        
