class FixedAgent:
    def __init__(self, character):
        self.character = character

    def choose_action(self, enemy=None):
        return "attack" #por ahora solo sabe atacar
