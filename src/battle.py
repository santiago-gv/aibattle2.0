import random

class Battle:
    def __init__(self, agent_a, agent_b, initiative_mode="probabilistic"):
        self.agent_a = agent_a
        self.agent_b = agent_b
        self.actions_log = []
        self._initiative_toggle = 0
        self._initiative_mode = initiative_mode  # "probabilistic" | "deterministic" | "alternate" | "simultaneous"

    def _choose_order(self, a, b, action_a, action_b):
        if self._initiative_mode == "simultaneous":
            return [("A", a, b, action_a), ("B", b, a, action_b)], True  # flag to apply damage simultaneously

        sa = a.character.get_speed()
        sb = b.character.get_speed()

        if self._initiative_mode == "probabilistic":
            total = sa + sb
            p_a = (sa / total) if total > 0 else 0.5
            first = "A" if random.random() < p_a else "B"
        elif self._initiative_mode == "alternate":
            first = "A" if (self._initiative_toggle % 2 == 0) else "B"
            self._initiative_toggle += 1
        else:  # deterministic
            first = "A" if sa >= sb else "B"

        if first == "A":
            return [("A", a, b, action_a), ("B", b, a, action_b)], False
        else:
            return [("B", b, a, action_b), ("A", a, b, action_a)], False

    def step(self):
        a = self.agent_a
        b = self.agent_b
        turn_index = len(self.actions_log) + 1

        state_a = a.get_state(b.character)
        state_b = b.get_state(a.character)

        action_a = a.choose_action(b.character)
        action_b = b.choose_action(a.character)

        # Defensas se activan antes de ataques
        if action_a == "defend":
            a.character.defend()
        if action_b == "defend":
            b.character.defend()

        order, simultaneous = self._choose_order(a, b, action_a, action_b)

        damage = {"A": 0, "B": 0}

        if simultaneous:
            # Ejecutar y acumular sin cancelar por KO
            for label, attacker, defender, action in order:
                if action == "attack":
                    dealt = attacker.character.attack(defender.character)
                elif action == "super_attack":
                    dealt = attacker.character.super_attack(defender.character)
                else:
                    dealt = 0
                damage[label] = dealt
        else:
            # Ordenado; si el defensor muere, se corta y evita doble KO
            for label, attacker, defender, action in order:
                if attacker.character.get_health() <= 0 or defender.character.get_health() <= 0:
                    continue
                if action == "attack":
                    dealt = attacker.character.attack(defender.character)
                elif action == "super_attack":
                    dealt = attacker.character.super_attack(defender.character)
                else:
                    dealt = 0
                damage[label] = dealt

        reward_a = damage["A"] - damage["B"]
        reward_b = damage["B"] - damage["A"]

        a_dead = a.character.get_health() <= 0
        b_dead = b.character.get_health() <= 0
        
        if b_dead and not a_dead:
            reward_a += 100
            reward_b -= 100
        elif a_dead and not b_dead:
            reward_b += 100
            reward_a -= 100

        self.actions_log.append(
            f"Torn {turn_index}: A={action_a} (dany={damage['A']}), B={action_b} (dany={damage['B']}) | "
            f"Salut A={a.character.get_health()}, Salut B={b.character.get_health()}"
        )

        next_state_a = a.get_state(b.character)
        next_state_b = b.get_state(a.character)
        a.update_q(state_a, action_a, reward_a, next_state_a)
        b.update_q(state_b, action_b, reward_b, next_state_b)

        a.character.reset_turn()
        b.character.reset_turn()

    def reset_episode(self):
        self.actions_log = []
        for c in [self.agent_a.character, self.agent_b.character]:
            c.health = 100
            c.reset_turn()
            c.cooldown = 3
        self._initiative_toggle = 0

    def get_actions_log(self):
        return self.actions_log