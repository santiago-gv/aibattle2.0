

class Battle:

    def __init__(self, learning_agent, fixed_agent):
        self.learning_agent = learning_agent
        self.fixed_agent = fixed_agent
        self.actions_log = []

    def step(self):
        
        learning_agent = self.learning_agent
        fixed_agent = self.fixed_agent.character
        turn_index = len(self.actions_log) + 1

        # Determinem ambdues accions abans d'aplicar efectes
        state = learning_agent.get_state(fixed_agent)
        action_agent = learning_agent.choose_action(fixed_agent)
        action_enemy = self.fixed_agent.choose_action()

        reward = 0
        damage_agent = 0
        damage_enemy = 0

        # Primer, apliquem les defenses per tal que
        # redueixin el dany d'aquest mateix torn
        if action_agent == "defend":
            learning_agent.character.defend()
        if action_enemy == "defend":
            fixed_agent.defend()

        # Ara apliquem els atacs amb les defenses ja actives
        if action_agent == "attack":
            damage_agent = learning_agent.character.attack(fixed_agent)


            reward += damage_agent
        elif action_agent == "super_attack":
            damage_agent = learning_agent.character.super_attack(fixed_agent)
            reward += damage_agent

        # Si l'enemic mor després de l'atac de l'agent
        if fixed_agent.get_health() <= 0:
            fixed_agent.health = 0
            reward += 100
            enemy_action_text = action_enemy if action_enemy else "cap acció"
            self.actions_log.append(
                f"Torn {turn_index}: Agent={action_agent} (dany={damage_agent}), Enemic={enemy_action_text} (dany=0) | Salut Agent={learning_agent.character.get_health()}, Salut Enemic={fixed_agent.get_health()}"
            )
            next_state = learning_agent.get_state(fixed_agent)
            learning_agent.update_q(state, action_agent, reward, next_state)
            learning_agent.character.reset_turn()
            fixed_agent.reset_turn()
            return

        # Apliquem l'atac de l'enemic si l'agent segueix viu
        if learning_agent.character.get_health() > 0:
            if action_enemy == "attack":
                damage_enemy = fixed_agent.attack(learning_agent.character)
            elif action_enemy == "super_attack":
                damage_enemy = fixed_agent.super_attack(learning_agent.character)


        # Reward restant basat en el dany rebut aquest torn
        reward -= damage_enemy

        # Log del torn
        enemy_action_text = action_enemy if action_enemy else "cap acció"
        self.actions_log.append(
            f"Torn {turn_index}: Agent={action_agent} (dany={damage_agent}), Enemic={enemy_action_text} (dany={damage_enemy}) | Salut Agent={learning_agent.character.get_health()}, Salut Enemic={fixed_agent.get_health()}"
        )

        # actualitzem Q-table
        next_state = learning_agent.get_state(fixed_agent)
        learning_agent.update_q(state, action_agent, reward, next_state)

        # resetejem estats de defensa
        learning_agent.character.reset_turn()
        fixed_agent.reset_turn()

    def reset_episode(self):
        self.actions_log = []
        for c in [self.learning_agent.character, self.fixed_agent.character]:
            c.health = 100
            c.attack_bonus = 0
            c.reset_turn()
            c.cooldown = 3

    def get_actions_log(self):
        return self.actions_log
