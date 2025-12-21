import random

# funcion para discretizar la vida de 10 en 10 para tener 11x11 estados (lo que dijo en clase)
def discretize(health):
    return max(0, min(10, health // 10))

class QLearningAgent:
    def __init__(self, character):
        self.character = character

        self.actions = ["attack", "defend"]
        self.q_table = {}
        
        self.alpha = 0.1 # tasa de aprendizaje (que tanto valoramos los nuevos estados)
        self.gamma = 0.9 # factor de descuento (que tanto valoramos el futuro)
        self.epsilon = 0.2 # tasa de exploración (que tanto exploramos vs explotamos)

    # obtenemos el estado actual basado en la salud del agente y del enemigo
    def get_state(self, enemy):
        return (discretize(self.character.get_health()), discretize(enemy.get_health()))

    def choose_action(self, enemy):
        state = self.get_state(enemy)

        # exploración vs explotación (con politica e-greedy)
        if random.random() < self.epsilon:
            return random.choice(self.actions)  

        q_attack = self.q_table.get((state, "attack"), 0)
        q_defend = self.q_table.get((state, "defend"), 0)

        # en caso de que sean iguales, elegimos aleatoriamente (no tenemos ningun estado para el caso)
        if q_attack == q_defend:
            return random.choice(self.actions)  

        # explotamos el mejor valor Q
        return "attack" if q_attack > q_defend else "defend"

    def update_q(self, state, action, reward, next_state):
        old_q = self.q_table.get((state, action), 0)
        future_q = max(
            self.q_table.get((next_state, "attack"), 0),
            self.q_table.get((next_state, "defend"), 0)
        )

        # actualizamos el valor Q usando la fórmula de Q-learning
        new_q = old_q + self.alpha * (reward + self.gamma * future_q - old_q)
        self.q_table[(state, action)] = new_q
